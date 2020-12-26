#!/bin/python3

from typing import List
import requests
import json
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def genprompt(q: str) -> str:
    def qaify(complicated: str, simplified: List[str]) -> str:
        return f"Explain: \"{complicated}\"\nSimple: {' '.join(simplified)} EOF\n"

    def qify(complicated: str) -> str:
        return f"Explain: \"{complicated}\"\n"

    ex1 = qaify(
        "Both Elephants and Rhinocerouses are pachyderms that eat shrubs.",
        [
          "Both Elephants and Rhinocerouses are pachyderms.",
          "Both Elephants and Rhinocerouses eat shrubs.",
        ]
    )

    ex2 = qaify(
        "Both ships ran out of food, driving the sailors to resort to cannabalism.",
        [
          "Both ships ran out of food.",
          "The sailors resorted to cannabalism."
        ]
    )

    ex3 = qaify(
        "The heart serves to pump blood in the body, drawing in oxygen poor blood from the veins and pumping it into the lungs.",
        [
          "The heart serves to pump blood in the body.",
          "The heart draws in oxygen poor blood from the veins.",
          "The heart pumps blood into the lungs."
        ]
    )

    prompt = "Task: Break down the complex sentence into simpler sentences.\n"

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


def gpt2complete(fact: str) -> List[str]:
    facts = []
    completions = requests.get('http://localhost:8080', data={
      'prompt': genprompt(fact),
      'nsequences': 1
    }).json()

    for c in completions:
        facts.extend(answerExtract(c))

    return facts

print(json.dumps(gpt2complete("Today is Thursday, and the test is on Friday.")))
print(json.dumps(gpt2complete("She had just bought two gorgeous dresses, so she needed to get matching shoes.")))
print(json.dumps(gpt2complete("I really want to see the game, but the mall is having a huge sale today.")))


