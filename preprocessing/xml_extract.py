def extract_start(x):
    return int(x["positioning"]["start"]["singlePosition"]["@index"])


def extract_end(x):
    return int(x["positioning"]["end"]["singlePosition"]["@index"])


def extract_type(x):
    return x["characterisation"]["type"]


def extract_embedded_schema(x):
    return x["positioning"]["embedded-schema"]


def extract_embedded_unit(x):
    return x["positioning"]["embedded-unit"]


def extract_term(x, item=0):
    assert item in [0, 1]
    return x["positioning"]["term"][item]["@id"]

