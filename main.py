#!/usr/bin/env python3
"""ClipEdit — クリップボード上の表を TSV / CSV / Markdown で相互変換する CLI。

使い方:
  python main.py auto   # 形式を自動判定して変換
  python main.py md     # → Markdown
  python main.py tsv    # → タブ区切り
  python main.py csv    # → CSV

AutoHotKey 例:
  RunWait, python "C:\\path\\to\\clipedit\\main.py" csv -q, , Hide
"""

from __future__ import annotations

import argparse
import sys

import clipboard_util
from converter import auto_convert, to_csv, to_markdown, to_tsv

MODES = ("auto", "md", "tsv", "csv")


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
    raise ValueError(f"unknown mode: {mode}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clipedit",
        description="クリップボードの表データを TSV / CSV / Markdown で相互変換する",
    )
    parser.add_argument(
        "mode",
        choices=MODES,
        help="auto=自動判定 / md=Markdownへ / tsv=タブ区切りへ / csv=CSVへ",
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
