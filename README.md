# ClipEdit

Excel / Google Sheets の表（TSV）・CSV・Markdown 表を、**クリップボード経由**で相互変換する CLI です。あわせて、数字・英数字・丸括弧 `()` の全角と半角を、指定した文字種だけ変換するモードがあります。

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

# 数字（０-９）だけ全角→半角
python main.py num

# 数字（0-9）だけ半角→全角
python main.py numzen

# 英数字（０-９ Ａ-Ｚ ａ-ｚ）だけ全角→半角
python main.py alnum

# 丸括弧（ ）だけ半角の () にする
python main.py paren
```

変換結果はクリップボードに書き戻されます。成功時は stderr に短いステータスが出ます。クリップボードが空、または表モードで表として読めないときは stderr に `error:` を出して終了コード 1 で戻ります。クリップボードの読み書きに失敗したときは終了コード 2 です。

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

; Ctrl+Shift+N : 数字だけ全角→半角
^+n::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" num -q', , "Hide")
}

; Ctrl+Alt+N : 数字だけ半角→全角
^!n::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" numzen -q', , "Hide")
}

; Ctrl+Shift+A : 英数字だけ全角→半角
^+a::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" alnum -q', , "Hide")
}

; Ctrl+Shift+P : 丸括弧だけ全角→半角
^+p::
{
    RunWait('python "C:\Users\kabuk\Documents\work\src\clipedit\main.py" paren -q', , "Hide")
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
| `num` | 任意のテキスト | 全角数字だけ半角。英字・記号・かな・括弧は残す |
| `numzen` | 任意のテキスト | 半角数字だけ全角。英字・記号・かな・括弧は残す |
| `alnum` | 任意のテキスト | 全角の英字と数字だけ半角。記号・かな・括弧は残す |
| `paren` | 任意のテキスト | 全角の丸括弧 `（）` だけを `()` にする。かぎ括弧などは残す |

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
