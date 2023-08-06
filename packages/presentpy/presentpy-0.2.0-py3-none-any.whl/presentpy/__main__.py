from pathlib import Path

import click

from presentpy.parser import process_notebook


@click.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
def process(file):
    path = Path(file)
    presentation = process_notebook(path)
    presentation.save(f"{path.stem}.pptx")


if __name__ == "__main__":
    process()
