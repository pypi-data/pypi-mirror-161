import json
import pathlib

import typer
from rich.console import Console
from rich.theme import Theme

try:
    from wa2rasa import (
        read_wa_object,
        intents_parser,
        entities_parser,
        save_rasa_yaml_file,
    )
except:  # for pytest
    from .wa2rasa import (
        read_wa_object,
        intents_parser,
        entities_parser,
        save_rasa_yaml_file,
    )

app = typer.Typer(
    name="wa2rasa",
    add_completion=False,
    help="Convert Watson Assistant skill object to rasa nlu.yml file.",
    pretty_exceptions_show_locals=False,
)

custom_theme = Theme({"info": "dim cyan", "warning": "magenta", "danger": "bold red"})
console = Console(theme=custom_theme)


@app.command()
def introduce_app(name: str = typer.Argument("bro", help="Your name.")):
    """App intro."""
    console.print(
        f"Hey {name}! This app helps you to convert your watson Assistant skill object to rasa nlu.yml file. For that, use the argument 'convert'.",
        style="info",
    )


@app.command()
def convert(
    wa_file: str = typer.Argument(
        ..., help="The path to your Watson Assistant json file."
    ),
    save_in: str = typer.Argument(
        ..., help="Path to the directory where you want to store the output."
    ),
    rasa_version: str = typer.Argument("3.1", help="The version of your rasa app."),
):
    """
    Convert Watson Assistant skill object to rasa nlu.yml file.
    """
    file_path = pathlib.Path(wa_file)
    if not file_path.absolute().is_file():
        console.print(f"File not found.", style="danger")
        raise Exception(
            f"Please verify that the file {str(file_path.absolute())} exists."
        )
    wa_object = read_wa_object(file_path=file_path.absolute())
    intents = wa_object.get("intents", [])
    entities = wa_object.get("entities", [])
    if intents:
        intents = intents_parser(intents)
    if entities:
        entities = entities_parser(entities)
    nlu_yml_obj = {"version": rasa_version, "nlu": intents + entities}
    if not entities:
        console.print(
            ":warning: No entity found in your Watson Assistant object.",
            style="warning",
        )
    if not intents:
        console.print(
            ":warning: No entities found in your Watson Assistant object.",
            style="warning",
        )
    file_path2 = pathlib.Path(save_in)
    if not file_path2.is_dir():
        console.print(f"Directory not found.", style="danger")
        raise Exception(
            f"Please verify that the directory {str(file_path2.absolute())} exists."
        )
    file_path2 = pathlib.Path(file_path2.absolute(), "nlu.yml")
    save_rasa_yaml_file(file_path=file_path2, object=nlu_yml_obj)
    console.print(f"Output saved in '{file_path2}'.", style="info")


if __name__ == "__main__":
    app()
