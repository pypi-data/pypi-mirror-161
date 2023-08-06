from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union

from dominate import tags as d


class FontSize(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()


class FontColors(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    IMPORTANT = auto()


def html_font_color(color: FontColors) -> str:
    colors = {
        FontColors.INFO: "black",
        FontColors.WARNING: "#ffca28;",
        FontColors.ERROR: "#C34A2C",
        FontColors.IMPORTANT: "#1967d3",
    }
    return colors.get(color, colors[FontColors.INFO])


def html_font_size(size: FontSize) -> str:
    fonts = {
        FontSize.SMALL: "16px",
        FontSize.MEDIUM: "18px",
        FontSize.LARGE: "20px",
    }
    return fonts.get(size, fonts[FontSize.MEDIUM])


class AlertComponent(ABC):
    @abstractmethod
    def html(self) -> d.html_tag:
        pass

    @abstractmethod
    def md(self, slack_format: bool) -> str:
        pass


@dataclass
class Text(AlertComponent):
    text: str
    size: FontSize = FontSize.MEDIUM
    color: FontColors = FontColors.INFO
    # HTML tag to place text in. e.g. div, p, h1, h2..
    tag: str = "div"
    
    def __post_init__(self):
        self.text = str(self.text)

    def html(self) -> d.html_tag:
        tag = getattr(d, self.tag)
        color = html_font_color(self.color)
        size = html_font_size(self.size)

        return tag(self.text, style=f"font-size:{size};color:{color};")

    def md(self, slack_format: bool) -> str:
        if slack_format:
            return self.slack_md()
        return self.classic_md()

    def classic_md(self) -> str:
        if self.size is FontSize.SMALL:
            return self.text
        if self.size is FontSize.MEDIUM:
            return f"## {self.text}"
        if self.size is FontSize.LARGE:
            return f"# {self.text}"

    def slack_md(self) -> str:
        if self.color in (FontColors.IMPORTANT, FontColors.ERROR):
            return f"*{self.text}*"
        return self.text


@dataclass
class KV(AlertComponent):
    data: Dict[str, Any]

    def html(self) -> d.html_tag:
        with (container := d.div()):
            for k, v in self.data.items():
                d.div(
                    d.span(
                        d.b(
                            Text(
                                f"{k}: ",
                                html_font_size(FontSize.LARGE),
                                html_font_color(FontColors.IMPORTANT),
                                "span",
                            ).html()
                        ),
                        Text(v, FontSize.LARGE, tag="span").html(),
                    )
                )
        return container

    def md(self, slack_format: bool) -> str:
        if slack_format:
            return self.slack_md()
        return self._md()

    def classic_md(self) -> str:
        rows = ["|||", "|---:|:---|"]
        for k, v in self.data.items():
            rows.append(f"|**{k}:**|{v}|")
        rows.append("|||")
        return "\n".join(rows)

    def slack_md(self) -> str:
        return "\n".join([f"*{k}:* {v}" for k, v in self.data.items()])


@dataclass
class Table(AlertComponent):
    rows: Union[List[List[str]], List[Dict[str, Any]]]
    caption: str
    header: Optional[List[str]] = None
    # an SQL query that was used to select `rows`
    query: str = None

    def __post_init__(self):
        self.caption = Text(self.caption, FontSize.LARGE, FontColors.IMPORTANT)

        kv_data = {"Total Rows": len(self.rows)}
        if self.query:
            kv_data["Query"] = self.query
        self.kv_data = KV(kv_data)

        if not self.header:
            # If header is not provided, rows should be dicts.
            self.header = []
            for row in self.rows:
                self.header += [f for f in row.keys() if f not in self.header]
        else:
            # If header is provided, rows may be lists.
            # Convert all row lists to dicts.
            for i, row in enumerate(self.rows):
                if isinstance(row, list):
                    self.rows[i] = dict(zip(self.header, row))

        # make sure all values are strings.
        for r in self.rows:
            for c in self.header:
                r[c] = str(r[c])

    def html(self, include_table_rows: bool = True):
        with (container := d.div(style="border:1px solid black;")):
            self.caption.html()
            self.kv_data.html()
            if include_table_rows:
                with d.div():
                    with d.table():
                        with d.tr():
                            for column in self.header:
                                d.th(column)
                        for row in self.rows:
                            with d.tr():
                                for column in self.header:
                                    d.td(row.get(column, ""))
        return container

    def md(self, slack_format: bool, include_table_rows: bool = True) -> str:
        if slack_format:
            return self.slack_md(include_table_rows)
        return self._md(include_table_rows)

    def classic_md(self, include_table_rows: bool) -> str:
        data = [self.caption.md()]
        if include_table_rows:
            table_rows = [self.header, [":----:" for _ in range(len(self.header))]] + [
                [row[col] for col in self.header] for row in self.rows
            ]
            table = "\n".join(["|".join(row) for row in table_rows])
            data.append(table)
        data.append(self.kv_data.md())
        return "\n\n".join(data).strip()

    def slack_md(self, include_table_rows: bool) -> str:
        data = [self.caption.slack_md()]
        if include_table_rows:
            rows = [dict(zip(self.header, self.header))] + self.rows
            # column width is length of longest string + a space of padding on both sides.
            columns_widths = {
                c: max(len(row[c]) for row in rows) + 2 for c in self.header
            }
            table = "\n".join(
                [
                    "|".join(
                        [
                            f"{{: ^{columns_widths[col]}}}".format(row[col])
                            for col in self.header
                        ]
                    )
                    for row in rows
                ]
            )
            data.append(table)
        data.append(self.kv_data.slack_md())
        return "\n\n".join(data).strip()
