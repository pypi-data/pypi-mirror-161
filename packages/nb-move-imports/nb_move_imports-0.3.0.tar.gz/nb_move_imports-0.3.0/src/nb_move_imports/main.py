import re
from itertools import filterfalse, tee
from typing import Callable, Iterable, List, Optional, Tuple, TypeVar

import click
import isort
import nbformat
from nbformat.notebooknode import NotebookNode

IMPORT_CELL_TAG = "IMPORT_CELL"
IGNORE_CELL_TAG = "IGNORE_MV_IMPORTS"
IMPORT_PATTERN = r"(?m)^(?:from[ ]+(\S+)[ ]+)?import[ ]+(\S+)[ ]*$"

T = TypeVar("T")


def _partition(
    pred: Callable[[T], bool], iterable: Iterable[T]
) -> Tuple[Iterable[T], Iterable[T]]:
    t1, t2 = tee(iterable)
    return filter(pred, t2), filterfalse(pred, t1)


def _is_import_line(line: str) -> bool:
    return re.match(IMPORT_PATTERN, line) is not None


def reorder_imoprt_statements(
    nb: NotebookNode, apply_isort: bool = False
) -> NotebookNode:
    """Reorder the import statements in the input notebook.

    Extract the imoprt statements from the cells of the input
    notebook and move them the first code cell.

    Args:
        nb (NotebookNode): Unsorted input notebook
        apply_isort (bool): Indication if the import statements should be sorted.
            Defaults to False.

    Returns:
        NotebookNode: Output notebook with reordered statements
    """
    code_cells = [
        c
        for c in nb["cells"]
        if (c["cell_type"] == "code")
        and (IGNORE_CELL_TAG not in c["metadata"].get("tags", []))
    ]

    # return if there are no code cells
    if not code_cells:
        return nb

    import_cells = [
        c for c in code_cells if IMPORT_CELL_TAG in c["metadata"].get("tags", [])
    ]

    # Select the first cell that is tagged with `IMPORT_CELL_TAG`.
    # If that does not exits select the first code cell
    if import_cells:
        import_cell = import_cells[0]
    else:
        import_cell = code_cells[0]
        metadata = import_cell["metadata"]
        tags = set(metadata.get("tags", []))
        tags.add(IMPORT_CELL_TAG)
        metadata["tags"] = list(tags)

    # extrac import statements
    all_import_lines: List[str] = []
    for cell in filter(lambda c: c is not import_cell, code_cells):
        lines = cell["source"].splitlines()
        i_lines, c_lines = _partition(_is_import_line, lines)
        all_import_lines.extend(i_lines)
        cell["source"] = "\n".join(c_lines)

    # add import staments to import cell
    import_statement = "\n".join(all_import_lines)
    new_cell_source = "\n".join([import_statement, import_cell["source"]])
    if apply_isort:
        new_cell_source = isort.code(new_cell_source)
    import_cell["source"] = new_cell_source
    return nb


@click.command()
@click.option("--sort", is_flag=True, help="Sort the import with isort")
@click.argument("input_path")
@click.argument("output_path", required=False)
def main(sort: bool, input_path: str, output_path: Optional[str] = None) -> None:
    """Main entry point for the nb_move_import script.

    Moves and sorts the import statements into the first cell of the Jupyter notebook
    under the specified path.

    Args:
        sort (bool): Indicates if the import statements should be sorted with isort
        input_path (str): Path where the unsorted jupyter notebook is stored.
        output_path (Optional[str]): Path where the sorted jupyter notebook is written to.
            If it is `None` then then the sorted notebook will be written back to the input
            path. Defaults to None.
    """
    nb = nbformat.read(input_path, as_version=4)
    print(f"Reoder notebook at '{input_path}'.")
    nb = reorder_imoprt_statements(nb, sort)
    output_path = input_path if output_path is None else output_path
    nbformat.write(nb, output_path)


if __name__ == "__main__":
    main()
