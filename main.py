#!/usr/bin/env python3
"""ClipEdit — クリップボード上の表変換と、文字種の全角・半角変換をする CLI。

使い方:
  python main.py auto    # 形式を自動判定して変換
  python main.py md      # → Markdown
  python main.py tsv     # → タブ区切り
  python main.py csv     # → CSV
  python main.py num     # 数字だけ全角→半角
  python main.py numzen  # 数字だけ半角→全角
  python main.py alnum   # 英数字だけ全角→半角
  python main.py paren   # 丸括弧 () だけ全角→半角

AutoHotKey 例:
  RunWait, python "C:\\path\\to\\clipedit\\main.py" csv -q, , Hide
"""

from __future__ import annotations

import argparse
import sys

import clipboard_util
from converter import (
    auto_convert,
    to_csv,
    to_fullwidth_digits,
    to_halfwidth_alnum,
    to_halfwidth_digits,
    to_halfwidth_parens,
    to_markdown,
    to_tsv,
)

MODES = ("auto", "md", "tsv", "csv", "num", "numzen", "alnum", "paren")


def convert(mode: str, text: str) -> tuple[str, str]:
    """
    変換を実行する。
    戻り値: (変換後テキスト, 人間向けの短い説明)
    """
    if mode == "auto":
        out, src, dst = auto_convert(text)
        return out, f"{src.name} -> {dst.name}"
    if mode == "md":
        return to_markdown(text), "-> MARKDOWN"
    if mode == "tsv":
        return to_tsv(text), "-> TSV"
    if mode == "csv":
        return to_csv(text), "-> CSV"
    if mode == "num":
        return to_halfwidth_digits(text), "digits FW -> HW"
    if mode == "numzen":
        return to_fullwidth_digits(text), "digits HW -> FW"
    if mode == "alnum":
        return to_halfwidth_alnum(text), "alnum FW -> HW"
    if mode == "paren":
        return to_halfwidth_parens(text), "paren FW -> HW"
    raise ValueError(f"unknown mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clipedit",
        description="クリップボードの表データ、または文字種（数字・英数字・丸括弧）を変換する",
    )
    parser.add_argument(
        "mode",
        choices=MODES,
        help=(
            "auto=自動判定 / md=Markdownへ / tsv=タブ区切りへ / csv=CSVへ / "
            "num=数字だけ全角→半角 / numzen=数字だけ半角→全角 / "
            "alnum=英数字だけ全角→半角 / paren=丸括弧だけ全角→半角"
        ),
    )
    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        dest="print_result",
        help="変換結果を標準出力にも表示する",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="ステータスメッセージを出さない（成功時は何も出さない）",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="クリップボードではなく標準入力から読む（結果は標準出力。クリップボードは更新しない）",
    )
    args = parser.parse_args(argv)

    try:
        if args.stdin:
            source = sys.stdin.read()
        else:
            source = clipboard_util.get_text()

        result, summary = convert(args.mode, source)

        if args.stdin:
            sys.stdout.write(result)
            if not result.endswith("\n"):
                sys.stdout.write("\n")
        else:
            clipboard_util.set_text(result)
            if args.print_result:
                print(result)
            if not args.quiet:
                lines = result.count("\n") + (1 if result else 0)
                print(f"ok: {summary} ({lines} lines)", file=sys.stderr)

    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
