#!/bin/python3

import requests
import json
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def qaify(question: str, answer:str) -> str:
    return f"Q: {question}\nA: {answer}\nEOF\n"

def qify(question: str) -> str:
    return f"Q: {question}"

def genprompt(x:str) -> [str]:
    return  (qaify(
      "Explain \"Elephants are related to Rhinocerouses\"",
      "Both Elephants and Rhinocerouses are pachyderms. Elephants and Rhinocerouses are large herbivores."
    ) +
    qaify(
      "Explain \"The heart is a component of the cardiovascular system\"",
      "The heart serves to pump blood in the body. The heart draws in oxygen poor blood from the veins and pumps it into the lungs."
      ) +
    qify( f"Explain \"{x}\"")
    )

def answerExtract(x:str) -> [str]:
    eprint (x)
    ans = x.split('EOF')[0].split(': ')[1]
    facts = []
    for s in ans.split('.'):
        s = s.strip()
        if s != '':
            facts.append(s)
    return facts

def gpt2complete(fact:str) -> [str]:
    facts = []
    completions = requests.get('http://localhost:8888', {
      'prompt': genprompt(fact),
      'nsequences':2
    }).json()

    for c in completions:
        facts.extend(answerExtract(c))

    return facts

def iter(fact:str, n:int):
    if n <= 0:
        return fact
    return {
      "root": fact,
      "child": list(map(lambda x: iter(x, n-1), gpt2complete(fact)))
    }

print(json.dumps(iter('The stock market crashed sunday', 2)))
