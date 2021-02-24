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

    # removing characters which ascii code is above 128
    # i'd say it's a bad approach... changing discourse size while iterating through it?
    # for i in range(len(discourse)):
    #     if ord(discourse[i]) >= 128: discourse = discourse[:i] + " " + discourse[i+1:]
    discourse = ''.join([x for x in discourse if ord(x) < 128])
    # still not sure if they didn't want to remove 127 as well

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

    edus = {x["@id"]: {
        "id": x["@id"],
        "type": xml_extract.extract_type(x),
        "text": discourse[xml_extract.extract_start(x):xml_extract.extract_end(x)],
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

