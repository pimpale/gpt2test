#!/usr/bin/env python3
# coding=utf-8
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import tornado.ioloop
import tornado.web


class GPTModel:

    def __init__(self, seed: int):
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        self.device = "cuda"
        self.gpt_model = "gpt2-xl"
        tokenizer = GPT2Tokenizer.from_pretrained(self.gpt_model)
        self.model = GPT2LMHeadModel.from_pretrained(self.gpt_model)
        self.model.to(self.device)

    def adjustlength(self, length: int) -> int:
        max_sequence_length = self.model.max_position_embeddings
        if length < 0 and max_sequence_length > 0:
            length = max_sequence_length
        elif 0 < max_sequence_length < length:
            # No generation bigger than model size
            length = max_sequence_length
        elif length < 0:
            length = MAX_LENGTH  # avoid infinite loop
        return length

    def generate(self,
                 prompt: str,
                 temperature: float,
                 rep_penalty: float,
                 nsequences: int,
                 length: int,
                 top_p: float,
                 top_k: float) -> [str]:

        encoded_prompt = tokenizer.encode(prompt, add_special_tokens=False,
                                          return_tensors="pt")
        encoded_prompt = encoded_prompt.to(self.device)

        if encoded_prompt.size()[-1] == 0:
            input_ids = None
        else:
            input_ids = encoded_prompt

        output_sequences = model.generate(
            input_ids=input_ids,
            max_length=self.adjustlength(length) + len(encoded_prompt[0]),
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
            decode_text = tokenizer.decode(generated_sequence.tolist(),
                                           clean_up_tokenization_spaces=True)
            decode_prompt = tokenizer.decode(encoded_prompt[0],
                                             clean_up_tokenization_spaces=True)

            ret.append(decode_text[len(decode_prompt):])
        return ret


class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.gpt_model = GPTModel(42)

    def get(self):
        self.gpt_model.generate(
            prompt=self.get_argument("prompt", ""),
            temperature=float(self.get_argument("temperature", "0.7")),
            rep_penalty=float(self.get_argument("repetition_penalty", "1")),
            nsequences=int(self.get_argument("nsequences", "1")),
            length=int(self.get_argument("length", "100")),
            top_p=float(self.get_argument("top_p", "0.9")),
            top_k=float(self.get_argument("top_k", "0")),
        )


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
