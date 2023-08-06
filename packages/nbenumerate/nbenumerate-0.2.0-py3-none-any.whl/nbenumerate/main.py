import re
from typing import List

import click
import nbformat
from nbformat.notebooknode import NotebookNode

from nbenumerate.version import Version

HEADING_PATTERN = r"^(?P<hashes>#+)\s*(?P<version>(\d+\.)*\d+\.?)?\s*(?P<title>.+)"


def _enumerate_text(text: str, version: Version) -> str:
    lines = text.split("\n")
    for i, line in enumerate(lines):
        # find header line
        m = re.match(HEADING_PATTERN, line)

        # containe if the line is no header
        if m is None:
            continue

        # parse title contents
        m_dict = m.groupdict()
        hashes, title = m_dict["hashes"], m_dict["title"]

        # calculate current version
        level = len(hashes)
        version.increment(level)

        # update title with version
        new_title = f"{hashes} {version} {title}"
        lines[i] = new_title

    return "\n".join(lines)


def _enumerate_notebook(nb: NotebookNode) -> NotebookNode:
    # get notebook cells
    markdown_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]

    # enumerate every notebook cell
    version = Version()
    for cell in markdown_cells:
        cell["source"] = _enumerate_text(cell["source"], version)
    return nb


@click.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
def main(files: List[str]) -> None:
    """Main entry point for `nbenumerate` script.

    Enumerate the markdown headings of all the jupyter notebooks that are
    passed in `files`.

    Args:
        files (List[str]): List of paths to jupyter notebooks
    """
    for file in files:
        nb = nbformat.read(file, as_version=4)
        enumerated_nb = _enumerate_notebook(nb)
        nbformat.write(enumerated_nb, file)


if __name__ == "__main__":
    main()
