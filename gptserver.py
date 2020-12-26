#!/usr/bin/env python3
# coding=utf-8
from typing import List
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tornado.ioloop
import tornado.web
import json


class GPTModel:

    def __init__(self, seed: int):
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        self.device = "cuda"
        self.gpt_model = "gpt2-xl"
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.gpt_model)
        self.model = GPT2LMHeadModel.from_pretrained(self.gpt_model)
        self.model.to(self.device)
        print("=== MODEL INITIALIZED === ")

    def adjustlength(self, length: int) -> int:
        max_sequence_length = self.model.config.max_position_embeddings
        if length < 0 and max_sequence_length > 0:
            length = max_sequence_length
        elif 0 < max_sequence_length < length:
            # No generation bigger than model size
            length = max_sequence_length
        elif length < 0:
            length = MAX_LENGTH  # avoid infinite loop
        return length

    def generate(self,
                 prompt_str: str,
                 temperature: float,
                 rep_penalty: float,
                 nsequences: int,
                 length: int,
                 top_p: float,
                 top_k: float) -> List[str]:

        eprompt = self.tokenizer.encode(prompt_str, add_special_tokens=False,
                                        return_tensors="pt")
        eprompt = eprompt.to(self.device)

        if eprompt.size()[-1] == 0:
            input_ids = None
        else:
            input_ids = eprompt

        output_sequences = self.model.generate(
            input_ids=input_ids,
            max_length=self.adjustlength(length) + len(eprompt[0]),
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=rep_penalty,
            do_sample=True,
            num_return_sequences=nsequences,
        )

        # Remove the batch dimension when returning multiple sequences
        if len(output_sequences.shape) > 2:
            output_sequences.squeeze_()

        ret = []
        for generated_sequence in output_sequences:
            # Decode text
            dtext = self.tokenizer.decode(generated_sequence.tolist(),
                                          clean_up_tokenization_spaces=True)
            dprompt = self.tokenizer.decode(eprompt[0],
                                            clean_up_tokenization_spaces=True)
            ret.append(dtext[len(dprompt):])
        return ret


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, model: GPTModel):
        self.gpt_model = model

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    def get(self):
        generated_sequences = self.gpt_model.generate(
            prompt_str=self.get_argument("prompt", ""),
            temperature=float(self.get_argument("temperature", "0.7")),
            rep_penalty=float(self.get_argument("repetition_penalty", "1")),
            # nsequences=int(self.get_argument("nsequences", "1")),
            nsequences=1,
            length=int(self.get_argument("length", "60")),
            top_p=float(self.get_argument("top_p", "0.9")),
            top_k=int(self.get_argument("top_k", "0")),
        )
        return self.write(json.dumps(generated_sequences))


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MainHandler, dict(model=GPTModel(42)))
    ])
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
