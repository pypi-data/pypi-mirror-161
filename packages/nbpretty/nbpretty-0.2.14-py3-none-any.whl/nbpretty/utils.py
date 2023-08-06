from pathlib import Path
from typing import Tuple, Any

import nbformat
from nbconvert import HTMLExporter


def ipynb_to_html(html_exporter: HTMLExporter, filename: Path) -> Tuple[str, Any]:
    """
    Convert a ipynb file to HTML text using an exporter
    """
    chapter_title = filename.name.lstrip("1234567890").lstrip(" ")[:-6]
    with filename.open() as infile:
        notebook = nbformat.read(infile, as_version=4)
        notebook["metadata"]["nbpretty"] = {"source_file": filename}
        notebook["metadata"]["chapter_title"] = chapter_title
        return html_exporter.from_notebook_node(notebook)
