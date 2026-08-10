"""クリップボードの読み書き（pyperclip 経由。Windows / macOS / Linux）。"""

from __future__ import annotations

import time

import pyperclip


def get_text() -> str:
    try:
        text = pyperclip.paste()
    except pyperclip.PyperclipException as exc:
        raise RuntimeError(f"クリップボードの読み取りに失敗しました: {exc}") from exc
    return text if text is not None else ""


def set_text(text: str, *, retries: int = 5, delay: float = 0.05) -> None:
    """
    クリップボードへ書き込む。
    他アプリがロックしている場合に備え、短いリトライを行う。
    """
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            pyperclip.copy(text)
            return
        except pyperclip.PyperclipException as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(f"クリップボードの書き込みに失敗しました: {last_error}")
