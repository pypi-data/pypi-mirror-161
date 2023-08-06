import sys
from pathlib import Path
from typing import List

import dominate
from dominate import tags as d
from premailer import transform

from .components import AlertComponent, Table
from .settings import logger


def use_inline_tables(tables: List[Table], inline_tables_max_rows: int) -> bool:
    """Check if tables are small enough to be displayed inline in the alert message.

    Args:
        tables (List[Table]): All tables that are to be used in the alert message.
        inline_tables_max_rows (int): Max number of table rows that can be used in the alert message.

    Returns:
        bool: Whether inline tables can be used.
    """
    if sum([len(t.rows) for t in tables]) < inline_tables_max_rows:
        return True
    return False


def attach_tables(tables: List[Table], attachments_max_size_mb: int) -> bool:
    """Check if tables are small enough to be attached as files.

    Args:
        tables (List[Table]): The tables that should be attached ass files.
        attachments_max_size_mb (int): Max total size of all attachment files.

    Returns:
        bool: Whether files can be attached.
    """
    tables_size_mb = sum([sys.getsizeof(t.rows) for t in tables]) / 10 ** 6
    if tables_size_mb < attachments_max_size_mb:
        logger.debug(f"Adding {len(tables)} tables as attachments.")
        return True
    else:
        logger.debug(
            f"Can not add tables as attachments because size {tables_size_mb}mb exceeds max {attachments_max_size_mb}"
        )
        return False


def render_components_html(
    components: List[AlertComponent], inline_tables_max_rows: int
) -> str:
    """Compile components into mailable HTML.

    Args:
        components (List[AlertComponent]): The components to include in the HTML.
        inline_tables_max_rows (int): Max number of table rows that can be used in the HTML.

    Returns:
        str: The generated HTML.
    """
    if not isinstance(components, (list, tuple)):
        components = [components]

    doc = dominate.document()
    with doc.head:
        d.style("body {text-align:center;}")
    # check size of tables to determine how best to process.
    tables = [c for c in components if isinstance(c, Table)]
    if len(tables):
        with doc.head:
            d.style(Path(__file__).parent.joinpath("styles", "table.css").read_text())

    include_table_rows = use_inline_tables(tables, inline_tables_max_rows)
    with doc:
        for c in components:
            d.div(
                c.html(include_table_rows=include_table_rows)
                if isinstance(c, Table)
                else c.html()
            )
            d.br()

    return transform(doc.render())


def render_components_md(
    components: List[AlertComponent], slack_format: bool, inline_tables_max_rows: int
) -> str:
    """Compile components to markdown.

    Args:
        components (List[AlertComponent]): The components to include in the Markdown.
        inline_tables_max_rows (int): Max number of table rows that can be used in the HTML.

    Returns:
        str: The generated markdown.
    """

    if not isinstance(components, (list, tuple)):
        components = [components]

    tables = [c for c in components if isinstance(c, Table)]

    include_table_rows = use_inline_tables(tables, inline_tables_max_rows)

    return "\n\n".join(
        [
            c.md(slack_format, include_table_rows)
            if isinstance(c, Table)
            else c.md(slack_format)
            for c in components
        ]
    ).strip()
