#!/bin/python3

from typing import List
import requests
import json
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def genprompt(q: str) -> str:
    def qaify(complicated: str, simplified: List[str]) -> str:
        return f"Complicated: {complicated}\nSimple: {' '.join(simplified)}\nEOF\n"

    def qify(complicated: str) -> str:
        return f"Complicated: {complicated}\n"

    ex1 = qaify(
        "Both Elephants and Rhinocerouses are pachyderms that eat shrubs.",
        [
          "Elephants are pachyderms.",
          "Rhinocerouses are pachyderms.",
          "Elephants eat shrubs.",
          "Rhinocerouses eat shrubs.",
        ]
    )

    ex2 = qaify(
        "The heart serves to pump blood in the body, drawing in oxygen poor blood from the veins and pumping it into the lungs.",
        [
          "The heart serves to pump blood in the body.",
          "The heart draws in oxygen poor blood from the veins.",
          "The heart pumps blood into the lungs."
        ]
    )

    return ex1 + ex2 + qify(q)


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


def gpt2complete(fact: str) -> List[str]:
    facts = []
    completions = requests.get('http://localhost:8888', data={
      'prompt': genprompt(fact),
      'nsequences': 1
    }).json()

    for c in completions:
        facts.extend(answerExtract(c))

    return facts


def iter(fact: str, n: int):
    if n <= 0:
        return fact
    return {
      "root": fact,
      "child": list(map(lambda x: iter(x, n-1), gpt2complete(fact)))
    }


print(json.dumps(iter('The stock market crashed Sunday', 2)))
