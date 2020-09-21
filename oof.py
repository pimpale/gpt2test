#!/bin/python3

import requests

mystr = """
Essay Brainstorm:
  * Elephants are majestic wildlife creatures
  * Elephants are related to Rhinocerouses
  * Elephants are Pachyderms
  * Elephants eat Grass
  * Elephants are endangered due to poaching
Essay:

Elephants are majestic wildlife creatures that eat grass. They are closely related to the Rhinocerous, and like them, are pachyderms. However, they are endangered due to poaching. 

Essay Brainstorm:
  * The heart is an organ
  * The heart is part of the cardiovascular system
  * Heart disease is responsible for 90% of deaths
Essay:
The heart is an organ that is part of the cardiovascular system. Heart disease is responsible for 90% of deaths.
"""

r = requests.get('http://localhost:8888', {
    'prompt': mystr,
    'length': 100,
    'nsequences': 2
})

for completion in r.json():
    print('==== RESPONSE ====')
    print(mystr, completion)
