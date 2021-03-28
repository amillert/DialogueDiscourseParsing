from preprocessing import files as pf
from preprocessing import dialogues as pd

import json
import os
import re
import sys


if __name__ == '__main__':
    _, input_dir, output_file = sys.argv

    dirs = os.listdir(
        input_dir if os.path.isdir(input_dir)
        else os.path.dirname(os.path.abspath(input_dir))
    )

    dialogues_cleaned = []

    for filename in dirs:
        path = os.path.join(os.path.join(input_dir, filename), "../../discourse/GOLD")
        abspath = os.path.abspath(path)

        # joining files based on prefix e.g. pilot_02_01, pilot_02_02, ... will be joined
        if os.path.exists(abspath):
            # for filename in os.listdir(abspath):
            if re.match("\S*.ac", filename):
                id = filename[:filename.find('_')]
                res = pf.process_file(id, os.path.join(abspath, filename[:filename.index(".")]))
                if res:
                    dialogues_cleaned.extend([pd.process_dialogue(dialogue) for dialogue in res])
                # dialogues.extend(pf.process_file(id, os.path.join(abspath, filename[:filename.index(".")])))

            # dialogues_cleaned = [pd.process_dialogue(dialogue) for dialogue in dialogues]
        else:
            if filename[0] != ".":
                id = filename.split("_")[0]
                res = [pf.process_file2(id, os.path.join(input_dir, filename))]
                if res:
                    dialogues_cleaned.extend([pd.process_dialogue(dialogue, True) for dialogue in res])
                # dialogues.append(res)

            # dialogues_cleaned = [pd.process_dialogue(dialogue, True) for dialogue in dialogues]

    with open(output_file, "w") as fout:
        fout.write(json.dumps(dialogues_cleaned))

    print(f"Cleaned {len(dialogues_cleaned)} dialogues")
