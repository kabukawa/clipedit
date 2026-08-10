"""TSV / CSV / Markdown 表の相互変換。"""

from __future__ import annotations

import csv
import io
import re
from enum import Enum, auto


class FormatKind(Enum):
    EMPTY = auto()
    MARKDOWN = auto()
    TSV = auto()
    CSV = auto()
    UNKNOWN = auto()


_MD_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")
_MD_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")


def detect_format(text: str) -> FormatKind:
    """文字列の表形式を推定する。"""
    if not text or not text.strip():
        return FormatKind.EMPTY

    lines = [
        ln
        for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if ln.strip()
    ]
    if not lines:
        return FormatKind.EMPTY

    md_like = sum(1 for ln in lines if _MD_ROW_RE.match(ln) or _MD_SEPARATOR_RE.match(ln))
    if md_like >= 2 or (md_like == 1 and len(lines) == 1 and "|" in lines[0]):
        if any(_MD_SEPARATOR_RE.match(ln) for ln in lines) or md_like >= 2:
            return FormatKind.MARKDOWN
        if all("|" in ln for ln in lines[: min(3, len(lines))]):
            return FormatKind.MARKDOWN

    # タブがあれば TSV 優先（Excel / Google Sheets のコピー）
    if any("\t" in ln for ln in lines):
        return FormatKind.TSV

    # カンマ区切り
    if any("," in ln for ln in lines[:3]):
        return FormatKind.CSV

    return FormatKind.UNKNOWN


def _normalize_newlines(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    while normalized.endswith("\n"):
        normalized = normalized[:-1]
    return normalized


def _parse_delimited(text: str, *, dialect: str) -> list[list[str]]:
    normalized = _normalize_newlines(text)
    if not normalized.strip():
        return []
    reader = csv.reader(io.StringIO(normalized), dialect=dialect)
    rows = [list(row) for row in reader]
    while rows and all(cell == "" for cell in rows[-1]):
        rows.pop()
    return rows


def _parse_tsv(text: str) -> list[list[str]]:
    """タブ区切りを 2 次元配列にする。"""
    return _parse_delimited(text, dialect="excel-tab")


def _parse_csv(text: str) -> list[list[str]]:
    """CSV を 2 次元配列にする。"""
    return _parse_delimited(text, dialect="excel")


def _split_md_row(line: str) -> list[str]:
    """Markdown の表行をセル配列に分割する。"""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    placeholder = "\x00"
    s = s.replace("\\|", placeholder)
    cells = [c.replace(placeholder, "|").strip() for c in s.split("|")]
    return cells


def _parse_markdown(text: str) -> list[list[str]]:
    """Markdown 表を 2 次元配列にする（セパレータ行は除く）。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    rows: list[list[str]] = []
    for line in lines:
        if not line.strip():
            continue
        if _MD_SEPARATOR_RE.match(line):
            continue
        if "|" not in line:
            continue
        rows.append(_split_md_row(line))
    return rows


def parse_table(text: str) -> tuple[list[list[str]], FormatKind]:
    """
    任意の表形式テキストを 2 次元配列にする。
    戻り値: (rows, 検出した形式)
    """
    kind = detect_format(text)
    if kind == FormatKind.EMPTY:
        raise ValueError("クリップボードが空です。")
    if kind == FormatKind.MARKDOWN:
        rows = _parse_markdown(text)
        if not rows:
            raise ValueError("Markdown の表が見つかりません。")
        return rows, kind
    if kind == FormatKind.TSV:
        rows = _parse_tsv(text)
        if not rows:
            raise ValueError("変換できる表データが見つかりません。")
        return rows, kind
    if kind == FormatKind.CSV:
        rows = _parse_csv(text)
        if not rows:
            raise ValueError("変換できる表データが見つかりません。")
        return rows, kind

    # UNKNOWN: タブ → カンマ → Markdown の順で試す
    if "\t" in text:
        rows = _parse_tsv(text)
        if rows:
            return rows, FormatKind.TSV
    if "," in text:
        rows = _parse_csv(text)
        if rows:
            return rows, FormatKind.CSV
    if "|" in text:
        rows = _parse_markdown(text)
        if rows:
            return rows, FormatKind.MARKDOWN
    raise ValueError("表形式として認識できません。")


def _escape_md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def rows_to_markdown(rows: list[list[str]], *, align_columns: bool = True) -> str:
    """2 次元配列を GFM 風 Markdown 表にする。"""
    if not rows:
        return ""

    width = max(len(r) for r in rows)
    normalized = [r + [""] * (width - len(r)) for r in rows]
    escaped = [[_escape_md_cell(c) for c in r] for r in normalized]

    if align_columns:
        col_widths = [max(len(escaped[r][c]) for r in range(len(escaped))) for c in range(width)]
        col_widths = [max(w, 3) for w in col_widths]

        def fmt_row(cells: list[str]) -> str:
            parts = [cells[i].ljust(col_widths[i]) for i in range(width)]
            return "| " + " | ".join(parts) + " |"

        header = fmt_row(escaped[0])
        sep = "| " + " | ".join("-" * col_widths[i] for i in range(width)) + " |"
        body = [fmt_row(r) for r in escaped[1:]]
    else:
        def fmt_row(cells: list[str]) -> str:
            return "| " + " | ".join(cells) + " |"

        header = fmt_row(escaped[0])
        sep = "| " + " | ".join("---" for _ in range(width)) + " |"
        body = [fmt_row(r) for r in escaped[1:]]

    if len(escaped) == 1:
        return "\n".join([header, sep])
    return "\n".join([header, sep, *body])


def rows_to_tsv(rows: list[list[str]]) -> str:
    """2 次元配列を Excel 向けタブ区切りにする。"""
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.writer(buf, dialect="excel-tab", lineterminator="\n")
    writer.writerows(rows)
    return buf.getvalue().rstrip("\n")


def rows_to_csv(rows: list[list[str]]) -> str:
    """2 次元配列を CSV（excel 方言）にする。"""
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.writer(buf, dialect="excel", lineterminator="\n")
    writer.writerows(rows)
    return buf.getvalue().rstrip("\n")


def to_markdown(text: str) -> str:
    """任意の表形式 → Markdown。"""
    rows, _ = parse_table(text)
    return rows_to_markdown(rows)


def to_tsv(text: str) -> str:
    """任意の表形式 → タブ区切り。"""
    rows, _ = parse_table(text)
    return rows_to_tsv(rows)


def to_csv(text: str) -> str:
    """任意の表形式 → CSV。"""
    rows, _ = parse_table(text)
    return rows_to_csv(rows)


# 後方互換エイリアス
def tsv_to_markdown(text: str) -> str:
    return to_markdown(text)


def markdown_to_tsv(text: str) -> str:
    rows = _parse_markdown(text)
    if not rows:
        raise ValueError("Markdown の表が見つかりません。")
    return rows_to_tsv(rows)


def auto_convert(text: str) -> tuple[str, FormatKind, FormatKind]:
    """
    形式を自動判定して相互変換する。
    - Markdown → TSV（シートへ貼りやすい）
    - TSV / CSV → Markdown
    戻り値: (変換後テキスト, 元形式, 先形式)
    """
    kind = detect_format(text)
    if kind == FormatKind.EMPTY:
        raise ValueError("クリップボードが空です。")
    if kind == FormatKind.MARKDOWN:
        return to_tsv(text), FormatKind.MARKDOWN, FormatKind.TSV
    if kind == FormatKind.TSV:
        return to_markdown(text), FormatKind.TSV, FormatKind.MARKDOWN
    if kind == FormatKind.CSV:
        return to_markdown(text), FormatKind.CSV, FormatKind.MARKDOWN

    rows, guessed = parse_table(text)
    if guessed == FormatKind.MARKDOWN:
        return rows_to_tsv(rows), FormatKind.MARKDOWN, FormatKind.TSV
    return rows_to_markdown(rows), guessed, FormatKind.MARKDOWN
