import json
import os
import random
import sys
import re


def random_subdialogization(dialogue, utterances_per_dialogue):
    id, edus, relations = dialogue.values()

    rnd = random.randint(0, len(edus) - utterances_per_dialogue)

    return {
        "id": id,
        "edus": {i: re.sub(r"^: ", "", edu["text"].strip())
                 for i, edu in enumerate(edus[rnd:rnd + utterances_per_dialogue], rnd)
        },
    }

    # return {
    #     "id": id,
    #     "edus": edus[rnd:rnd + utterances_per_dialogue],
    #     "ranges": f"{rnd},{rnd+utterances_per_dialogue}",
    #     "relations": relations
    # }

if __name__ == "__main__":
    # sampling and saving json
    path, k, u = sys.argv[1:]
    num_dialogues = int(k)
    utterances_per_dialogue = int(u)

    abspath = os.path.abspath(path)

    dzejson = json.loads(open(abspath, "r").read())
    random_dialogues = random.sample(dzejson, num_dialogues)  # list of dicts

    final_dialogues = list(map(lambda l: random_subdialogization(l, utterances_per_dialogue), random_dialogues))

    os.makedirs("subdialogues", exist_ok=True)
    for dial in final_dialogues:
        with open(f"subdialogues/{dial['id']}", "w") as fout:
            fout.writelines(json.dumps(dial, indent=2))
    
    # parsing user's input and rejoining with samples
    # save annotation in separate file in format:
    # x, y, relation_type
