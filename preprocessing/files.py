from preprocessing import xml_extract

import xmltodict


def merge_dialogues(schema, edus, belong_to, buf_dialogues):
    for item in schema:
        if not item["positioning"]: continue

        cdu = []
        if "embedded-unit" in item["positioning"]:
            if isinstance(xml_extract.extract_embedded_unit(item), list):
                cdu = [unit["@id"] for unit in xml_extract.extract_embedded_unit(item)]
                # cdu = [unit["@id"] for unit in extract_embedded_unit(item) if unit["@id"] in edus]
            else:
                cdu = [xml_extract.extract_embedded_unit(item)["@id"]]

            cdu = [edu for edu in cdu if edu in edus]

        if "embedded-schema" in item["positioning"]:
            if isinstance(xml_extract.extract_embedded_schema(item), list):
                cdu += [unit["@id"] for unit in xml_extract.extract_embedded_schema(item)]
            else:
                cdu += [xml_extract.extract_embedded_schema(item)["@id"]]

        _id = item["@id"]

        belong_to[_id] = belong_to[cdu[0]]
        buf_dialogues[belong_to[_id]]["cdus"][_id] = cdu

    return schema, edus, belong_to, buf_dialogues


def find_belonging(edus, buf_dialogues):
    belong_to = {}
    for id_edu, edu in edus.items():
        found = False
        for id_dialogue in buf_dialogues:
            dialog = buf_dialogues[id_dialogue]
            if dialog["start"] <= edu["start"] and dialog["end"] >= edu["end"]:
                found = True
                dialog["edus"][id_edu] = edu
                belong_to[id_edu] = id_dialogue
                break
        if not found:
            raise Warning("Dialogue not found")

    return belong_to


def handle_response(resp):
    opening = resp.find("(")
    return resp[opening + 1:-1] if opening != -1 else resp


def annotate_utterance(line):
    tmp = line.split("\t")
    if len(tmp) == 4:
        return tmp[0], tmp[1], tmp[2], normalize(handle_response(tmp[3]))


def normalize(text):
    # TODO(albert): sth messed up w/ this. different results from previous approach
    # removing characters which ascii code is above 128
    # i'd say it's a bad approach... changing discourse size while iterating through it?
    # for i in range(len(discourse)):
    #     if ord(discourse[i]) >= 128: discourse = discourse[:i] + " " + discourse[i+1:]
    # still not sure if they didn't want to remove 127 as well
    return ''.join([" " if ord(x) >= 128 else x for x in text]).strip()


def reformat(dics, identifier):
    global_start = min([float(x["start"]) for x in dics])
    global_end = max([float(x["stop"]) for x in dics])
    res = {
        "id": identifier,
        "start": global_start,
        "end": global_end,
        "edus": {},
        "cdus": {},
        "relations": []
    }

    for ix, dic in enumerate(dics):
        id = f"DAIC-{identifier}-{ix}"
        res["edus"][id] = {
            "id": id,
            "type": "paragraph",
            "speaker": dic['speaker'],
            "text": f" : {dic['speaker']} : {dic['value']}",
            "start": dic["start"],
            "end": dic["stop"]
        }
        if ix + 1 == len(dics):
            break
        elif dic["speaker"] == dics[ix + 1]["speaker"]:
            res["relations"].append({"type": "Continuation", "x": ix, "y": ix + 1})
        elif dic["speaker"] != dics[ix + 1]["speaker"] and "?" in dic["value"]:
            res["relations"].append({"type": "QA-pair", "x": ix, "y": ix + 1})
        elif dic["speaker"] != dics[ix + 1]["speaker"]:
            res["relations"].append({"type": "wymiana zdań", "x": ix, "y": ix + 1})
        else:
            res["relations"].append({"type": "not assigned", "x": ix, "y": ix + 1})

    # TODO(albert): there are originally also relations (18), and cdus (3);
    #               whereas edus - 36
    #               relations is like type (question-answer, acknowledgment, etc. and then x, y pairs of ids)

    return res


def process_file2(identifier, filename_prefix):
    keys = ["start", "stop", "speaker", "value"]
    dics = []
    with open(filename_prefix, "r") as f_annotation:
        annotations = f_annotation.readlines()
        for line in annotations[1:]:
            res = annotate_utterance(line.strip())
            if res:
                dics.append(dict(zip(keys, res)))

    reformatted = reformat(dics, identifier)

    return reformatted


def process_file(identifier, filename_prefix):
    with open(f"{filename_prefix}.aa", "r") as f_annotation:
        # xml in ordered dicts
        annotations = xmltodict.parse(''.join(f_annotation.readlines()))["annotations"]

    schema = annotations["schema"] if "schema" in annotations else []
    units = annotations["unit"]
    relations = [] if "relation" not in annotations else annotations["relation"]

    if not isinstance(schema, list):
        schema = [schema]
    if not isinstance(relations, list):
        relations = [relations]  # I guess if it's not given by schema

    with open(f"{filename_prefix}.ac", "r") as f_discourse:
        discourse: str = f_discourse.readline()  # one-liner - so res in str not list

    discourse = normalize(discourse)

    exclude_types = ["Turn", "NonplayerTurn"]

    pre_buf = filter(lambda x: xml_extract.extract_type(x) == "Dialogue", units)
    pre_edu = filter(lambda x: xml_extract.extract_type(x) not in exclude_types + ["Dialogue"], units)

    buf_dialogues = {x["@id"]: {
        "start": xml_extract.extract_start(x),
        "end": xml_extract.extract_end(x),
        "edus": {},
        "cdus": {},
        "relations": [],
    } for x in pre_buf}

    # check those extracts
    edus = {x["@id"]: {
        "id": x["@id"],
        "type": xml_extract.extract_type(x),
        "text": discourse[xml_extract.extract_start(x)-1:xml_extract.extract_end(x)-1].strip(),
        "start": xml_extract.extract_start(x),
        "end": xml_extract.extract_end(x),
    } for x in pre_edu}

    belong_to = find_belonging(edus, buf_dialogues)

    schema, edus, belong_to, buf_dialogues = merge_dialogues(schema, edus, belong_to, buf_dialogues)

    for item in relations:
        _id = item["@id"]
        x = xml_extract.extract_term(item)
        y = xml_extract.extract_term(item, 1)
        buf_dialogues[belong_to[x]]["relations"].append({
            "type": xml_extract.extract_type(item),
            "x": x,
            "y": y
        })

    for _id in buf_dialogues:
        buf_dialogues[_id]["id"] = identifier
        yield buf_dialogues[_id]
