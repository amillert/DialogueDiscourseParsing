import json
import os
import random
import sys


def random_subdialogization(dialogue, utterances_per_dialogue):
    id, edus, relations = dialogue.values()

    rnd = random.randint(0, len(edus) - utterances_per_dialogue)

    return {
        "id": id,
        "euds": edus[rnd:rnd + utterances_per_dialogue],
        "relations": relations
    }

if __name__ == "__main__":
    path, k, u = sys.argv[1:]
    num_dialogues = int(k)
    utterances_per_dialogue = int(u)

    abspath = os.path.abspath(path)

    dzejson = json.loads(open(abspath, "r").read())
    random_dialogues = random.sample(dzejson, num_dialogues)  # list of dicts

    final_dialogues = list(map(lambda l: random_subdialogization(l, utterances_per_dialogue), random_dialogues))
