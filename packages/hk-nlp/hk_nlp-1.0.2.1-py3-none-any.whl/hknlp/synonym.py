from typing import List
import random
import json
import os


SYN_PATH = os.path.join(os.path.abspath(__file__), "data/synonyms.json")


def read_json(path: str) -> dict or list:
    with open(path, 'r', encoding='utf-8') as r:
        return json.load(r)


class SynonymReplacement:
    def __init__(self, tokenize_function):
        self.synonyms = read_json(SYN_PATH)
        self.rng = random.SystemRandom()
        self.tokenize = tokenize_function

    def convert(self, text: str) -> List[str]:
        text = text.replace(" ", "_SP_")
        outputs = [self.rng.choice(self.synonyms.get(token, [token]))
                   for token in self.tokenize(text)]

        return "".join(outputs).replace("_SP_", " ")