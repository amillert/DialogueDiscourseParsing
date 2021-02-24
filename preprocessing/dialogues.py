def get_head(x, has_incoming, dialogue):
    if x in dialogue["edus"]:
        return x
    else:
        for du in dialogue["cdus"][x]:
            if not du in has_incoming: return get_head(du, has_incoming, dialogue)
        raise Warning("Can't find the recursive head")


def clean_dialogues(dialogue):
    dialogue_cleaned = {
        "id": dialogue["id"],
        "edus": [],
        "relations": []
    }

    for edu in dialogue["edu_list"]:
        dialogue_cleaned["edus"].append({
            "speaker": edu["speaker"],
            "text": edu["text"]
        })
    for relation in dialogue["relations"]:
        dialogue_cleaned["relations"].append({
            "type": relation["type"],
            "x": relation["x"],
            "y": relation["y"]
        })

    return dialogue_cleaned


def process_dialogue(dialogue):
    has_incoming = {}

    for relation in dialogue["relations"]:
        has_incoming[relation["y"]] = True

    for _id in dialogue["edus"]:
        edu = dialogue["edus"][_id]
        if edu["type"] == "paragraph": continue

        for _id_para in dialogue["edus"]:
            para = dialogue["edus"][_id_para]
            if para["type"] != "paragraph": continue
            if para["start"] <= edu["start"] and para["end"] >= edu["end"]:
                edu["speaker"] = para["text"].split()[2]

    dialogue["edu_list"] = []
    for _id in dialogue["edus"]:
        if dialogue["edus"][_id]["type"] != "paragraph":
            dialogue["edu_list"].append(dialogue["edus"][_id])
    dialogue["edu_list"] = sorted(dialogue["edu_list"], key=lambda edu: edu["start"])

    idx = {dialogue["edu_list"][i]["id"]: i for i in range(len(dialogue["edu_list"]))}

    for i, edu in enumerate(dialogue["edu_list"]):
        print(i, edu["speaker"], ":", edu["text"])

    print("===")

    for relation in dialogue["relations"]:
        relation["x"] = idx[get_head(relation["x"], has_incoming, dialogue)]
        relation["y"] = idx[get_head(relation["y"], has_incoming, dialogue)]

    return clean_dialogues(dialogue)
