import json

import yaml

# https://stackoverflow.com/questions/45004464/yaml-dump-adding-unwanted-newlines-in-multiline-strings
class PSS(str):
    pass


def pss_representer(dumper, data):
    style = "|"
    tag = "tag:yaml.org,2002:str"
    return dumper.represent_scalar(tag, data, style=style)


yaml.add_representer(PSS, pss_representer, Dumper=yaml.SafeDumper)


def read_wa_object(file_path):
    with open(file_path, "r") as file:
        wa_object = json.load(file)
    return wa_object


def save_rasa_yaml_file(file_path, object):
    outputfile = open(file_path, "w")
    yaml.safe_dump(object, outputfile, allow_unicode=True, sort_keys=False)
    outputfile.close()


def clean_example(example):
    return example.replace("'", "").replace('"', "").replace(":", "")


def intents_parser(intents):
    for i, intent in enumerate(intents):
        clean_examples = [
            "- " + clean_example(example["text"]) + "\n"
            for example in intent["examples"]
        ]
        intents[i]["examples"] = PSS("".join(clean_examples))
        if type(intent.get("description")) == str:
            del intents[i]["description"]
    return intents


def build_rasa_entity(entity_name, value_name, values, type="synonym"):
    examples = PSS("".join(["- " + value + "\n" for value in values]))
    rasa_entity = {
        type: f"{entity_name}_{value_name}",
        "examples": examples,
    }
    return rasa_entity


def entities_parser(entities):
    obj_entities = []
    for entity in entities:
        entity_name = entity["entity"]
        for value in entity["values"]:
            if value["type"] == "synonyms":
                value_name = value["value"]
                values = value.get("synonyms", []) + [value_name]
                rasa_entity = build_rasa_entity(entity_name, value_name, values)
                obj_entities.append(rasa_entity)
            if value["type"] == "patterns":
                value_name = value["value"]
                values = value["patterns"]
                rasa_entity = build_rasa_entity(
                    entity_name, value_name, values, type="regex"
                )
                obj_entities.append(rasa_entity)
    return obj_entities
