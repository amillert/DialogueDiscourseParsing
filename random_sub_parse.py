import json
import os
import sys

from collections import namedtuple


annotation_tupple = namedtuple("AnnotationTupple", "dialogue_idx x y relation")

def load_json(path):
    return json.loads(open(path, "r").read())

def verify_not_dir_and_load(path, pardir):
    path_to_verify = os.path.join(pardir, path)
    if not os.path.isdir(path_to_verify):
        return path_to_verify
    else:
        return
    

def list_dir(path):
    return list(
        filter(
            lambda l: l,  # remove those which yield None (e.g. subdialogues/annotated, namely - dirs)
            map(
                lambda l: verify_not_dir_and_load(l, os.path.abspath(path)),
                os.listdir(path)
            )
        )
    )

def load_annotations_to_tupples(path):
    dialogue_idx = path.split("/")[-1]
    return list(
        map(
            lambda line: annotation_tupple(* ([dialogue_idx] + line.strip().split(", "))),
            open(path, "r").readlines()
        )
    )

def drop_processed_annotation(annotated, id):
    return list(filter(lambda l: l[0].dialogue_idx != id, annotated))

def check_if_id_in_annotated_and_provide_rel(id, annotated):
    worked = False
    for a in annotated:
        if a[0].dialogue_idx == id:
            worked = True
            break

    if worked:
        return [(ai.x, ai.y, ai.relation) for ai in a], drop_processed_annotation(annotated, id)
    return None, annotated

    # res = next(map(lambda l: (l.x, l.y, l.relation), filter(lambda a: a.dialogue_idx == id, annotated)))

def join_dialogue_with_annotations(random_dialogues, annotated):
    for i, dialogue in enumerate(random_dialogues):
        rel, annotated = check_if_id_in_annotated_and_provide_rel(dialogue["id"], annotated)
        if rel:
            # relations are originally strings not indices
            random_dialogues[i]["realtions"] = [{"x": int(x), "y": int(y), "type": relation} for x, y, relation in rel]
        else:
            random_dialogues[i]["realtions"] = []

    return random_dialogues

if __name__ == "__main__":
    path_json_dir, path_annotations = sys.argv[1:]

    random_dialogues = list(map(load_json, list_dir(path_json_dir)))
    annotated = list(map(load_annotations_to_tupples, list_dir(path_annotations)))

    random_annotated = join_dialogue_with_annotations(random_dialogues, annotated)

    annotated_json = json.dumps(random_annotated)  # , indent=2)
    # indent <- only for readibility but it must be joined for parser to work

    save_path = f"{path_annotations}/joined"
    os.makedirs(save_path, exist_ok=True)
    with open(f"{save_path}/random_joined_annotated", "w") as fout:
        # fout.write(json.dumps(annotated_json, indent=2))
        fout.write(annotated_json)
