# ClipEdit

Excel / Google Sheets の表（TSV）・CSV・Markdown 表を、**クリップボード経由**で相互変換する CLI です。

タスクトレイ常駐はしません。AutoHotKey などからホットキーで呼び出す想定です。Windows / macOS / Linux で動きます。

## 使い方

```bash
pip install -r requirements.txt

# 自動判定（Markdown ↔ TSV、CSV → Markdown）
python main.py auto

# 任意の表 → Markdown
python main.py md

# 任意の表 → タブ区切り
python main.py tsv

# 任意の表 → CSV
python main.py csv
```

変換結果はクリップボードに書き戻されます。成功時は stderr に短いステータスが出ます。

| オプション | 説明 |
|------------|------|
| `-q` / `--quiet` | ステータスを出さない |
| `-p` / `--print` | 結果を標準出力にも表示 |
| `--stdin` | 標準入力から読み、標準出力へ書く（クリップボードは使わない） |

### パイプ（OS 共通）

```bash
echo -e "a\tb\n1\t2" | python main.py md --stdin
```

## AutoHotKey からの呼び出し例

```ahk
; Ctrl+Shift+M : 表 → Markdown
^+m::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" md -q', , "Hide")
}

; Ctrl+Shift+T : Markdown → タブ区切り
^+t::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" tsv -q', , "Hide")
}

; Ctrl+Shift+V : 自動変換
^+v::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" auto -q', , "Hide")
}

; Ctrl+Shift+C : → CSV
^+c::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" csv -q', , "Hide")
}
```

venv を使う場合は `python` を `.venv\Scripts\python.exe` のフルパスに置き換えてください。

## モード

| モード | 入力 | 出力 |
|--------|------|------|
| `auto` | 自動判定 | Markdown ↔ TSV（CSV は Markdown へ） |
| `md` | TSV / CSV / Markdown | Markdown 表 |
| `tsv` | TSV / CSV / Markdown | タブ区切り |
| `csv` | TSV / CSV / Markdown | CSV |

## 依存

- Python 3.10+
- [pyperclip](https://github.com/asweigart/pyperclip)

Linux では `xclip` または `xsel`（Wayland なら `wl-clipboard`）が必要な場合があります。

## テスト

```bash
python -m unittest test_converter.py -v
```

## ライセンス

MIT
