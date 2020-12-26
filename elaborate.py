#!/bin/python3

from typing import List
import requests
import json
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def genprompt(q: str) -> str:
    def qaify(question: str, answer: str) -> str:
        return f"Q: {question}\nA: {answer}\nEOF\n"

    def qify(question: str) -> str:
        return f"Q: {question}"

    ex1 = qaify(
        "Explain \"Elephants are related to Rhinocerouses.\"",
        "Both Elephants and Rhinocerouses are pachyderms. Elephants and Rhinocerouses are large herbivores."
    )

    ex2 = qaify(
        "Explain \"The heart is a component of the cardiovascular system.\"",
        "The heart serves to pump blood in the body. The heart draws in oxygen poor blood from the veins and pumps it into the lungs."
    )

    return ex1 + ex2 + qify(f"Explain \"{q}\"")


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
    completions = requests.get('http://localhost:8080', data={
      'prompt': genprompt(fact),
      'nsequences': 2
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


print(json.dumps(iter('The stock market crashed Sunday.', 2)))
