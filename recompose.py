#!/bin/python3

from typing import List
import requests
import json
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def genprompt(q: List[str]) -> str:
    def qaify(simples: List[str], complicated: str) -> str:
        return f"Input: {chr(14).join(simples)}\n\nOutput: {complicated}\nEOF\n"

    def qify(simples: List[str]) -> str:
        return f"Input: {chr(14).join(simples)}\n"

    ex1 = qaify(
        ["The beach is a lot of fun.", "The mountains are better."],
        "The beach is a lot of fun, yet the mountains are better."
    )

    ex2 = qaify(
        ["A group of us went to the movie.", "We agreed it was enjoyable."],
        "A group of us went to the movie, and we agreed it was enjoyable.",
    )

    ex3 = qaify(
        ["Today is Thursday.", "The test is on Friday."],
        "Today is Thursday, and the test is on Friday.",
    )

    prompt = "Join sentences together to form a more complex sentence.\n\n"

    return prompt + ex1 + ex2 + ex3 + qify(q)


def answerExtract(x: str) -> List[str]:
    eprint(x)
    eprint("====")
    ans = x.split('EOF')[0].split(': ')[1]
    facts = []
    for s in ans.split('.'):
        s = s.strip()
        if s != '':
            facts.append(s)
    return facts


def gpt2completeSimples(fact: List[str]) -> List[str]:
    facts = []
    completions = requests.get('http://localhost:8080', data={
      'prompt': genprompt(fact),
      'nsequences': 2
    }).json()

    for c in completions:
        facts.extend(answerExtract(c))

    return facts


print(json.dumps(gpt2completeSimples([
    'The stock market crashed Sunday.',
    'Ford stock prices dipped below $40.'
])))

print(json.dumps(gpt2completeSimples([
    'I really want to see the game.',
    'The mall is having a huge sale today.'
])))
