from functools import partial
import importlib.metadata
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict

import click
from livereload import Server
from rich.logging import RichHandler
from rich.progress import track
from yaml import safe_load

from nbconvert import HTMLExporter
from nbconvert.preprocessors import tagremove
from traitlets.config import Config

from . import preprocessors, toc, utils

__version__ = importlib.metadata.version(__package__)


@click.command()
@click.argument("directory", type=Path)
@click.option('--prompt/--no-prompt', default=True, help="Should the output contain the IPython prompt")
@click.option('--serve', is_flag=True, help="Serve the pages to the browser")
def build(directory: Path, prompt: bool, serve: bool):
    """
    Convert notebooks in DIRECTORY
    """

    if not directory.exists() or not directory.is_dir():
        ctx = click.get_current_context()
        ctx.fail(f"Directory {directory.resolve()} does not exist")

    _build(directory, prompt)

    if serve:
        server = Server()
        server.watch(f"{str(directory)}/*.ipynb", partial(_build, directory, prompt))
        server._setup_logging = lambda: None  # https://github.com/lepture/python-livereload/issues/232
        server.serve(root=directory, open_url_delay=1)


def _build(directory: Path, prompt: bool):
    logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)])
    logger = logging.getLogger("nbpretty")

    mod_dir = Path(os.path.abspath(os.path.dirname(__file__)))

    config = Config()
    config.TagRemovePreprocessor.remove_cell_tags = {"remove_cell"}
    config.TagRemovePreprocessor.remove_input_tags = {"remove_input"}
    config.TemplateExporter.exclude_input_prompt = not prompt
    config.TemplateExporter.exclude_output_prompt = not prompt
    config.TemplateExporter.extra_template_basedirs = [mod_dir / "templates"]
    config.Exporter.optimistic_validation = True

    chapters = sorted(f for f in directory.glob("*.ipynb") if re.match(r"\d\d.*", f.name))
    answers = sorted(f for f in directory.glob("answer_*.ipynb"))
    asides = sorted(f for f in directory.glob("aside_*.ipynb"))
    appendixes = sorted(f for f in directory.glob("appendix_*.ipynb"))

    try:
        with (directory / "config.yaml").open() as f:
            nbpretty_config = safe_load(f)
            course_title = nbpretty_config["course_title"]
            custom_blocks = nbpretty_config.get("custom_blocks")
            try:
                extra_css_file = nbpretty_config["extra_css_file"]
            except KeyError:
                extra_css_file = None
    except FileNotFoundError:
        ctx = click.get_current_context()
        ctx.fail(f"config.yaml could not be found")

    logger.info("Constructing table of contents")
    toc_html = toc.construct_toc(chapters, config)

    html_exporter = HTMLExporter(template_name="nbpretty", config=config)
    html_exporter.register_preprocessor(tagremove.TagRemovePreprocessor, enabled=True)
    html_exporter.register_preprocessor(preprocessors.PageLinks(chapters), enabled=True)
    html_exporter.register_preprocessor(preprocessors.HighlightExercises, enabled=True)
    html_exporter.register_preprocessor(preprocessors.SetTitle(course_title), enabled=True)
    html_exporter.register_preprocessor(preprocessors.HideWriteFileMagic, enabled=True)
    html_exporter.register_preprocessor(preprocessors.FixLinkExtensions, enabled=True)
    html_exporter.register_preprocessor(preprocessors.CustomBlocks(custom_blocks), enabled=True)
    html_exporter.register_preprocessor(preprocessors.InsertTOC(toc_html), enabled=True)
    html_exporter.register_preprocessor(preprocessors.UninlineCss, enabled=True)
    html_exporter.register_preprocessor(preprocessors.AddExtraCss(extra_css_file), enabled=extra_css_file is not None)

    output_directory = directory

    extra_files: Dict[Path, str] = {}

    all_files = chapters + answers + asides + appendixes

    for filename in track(all_files):
        body, resources = utils.ipynb_to_html(html_exporter, filename)
        extra_files.update(resources["files"])
        with open(output_directory / f"{resources['output_stem']}.html", "w") as out:
            logger.info(f"Writing '{filename}' as '{out.name}'")
            out.write(body)

    for filename, contents in extra_files.items():
        with (output_directory / filename).open("w") as f:
            f.write(contents)


def main():
    build()


if __name__ == "__main__":
    main()
