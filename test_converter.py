"""converter のユニットテスト。"""

from __future__ import annotations

import unittest

from converter import (
    FormatKind,
    auto_convert,
    detect_format,
    markdown_to_tsv,
    to_csv,
    to_markdown,
    to_tsv,
    tsv_to_markdown,
)


class TestDetect(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(detect_format(""), FormatKind.EMPTY)
        self.assertEqual(detect_format("   \n  "), FormatKind.EMPTY)

    def test_tsv(self) -> None:
        self.assertEqual(detect_format("a\tb\nc\td"), FormatKind.TSV)

    def test_csv(self) -> None:
        self.assertEqual(detect_format("a,b\nc,d"), FormatKind.CSV)

    def test_markdown(self) -> None:
        md = "| a | b |\n| --- | --- |\n| c | d |"
        self.assertEqual(detect_format(md), FormatKind.MARKDOWN)


class TestConvert(unittest.TestCase):
    def test_tsv_to_md_basic(self) -> None:
        tsv = "Name\tAge\nAlice\t30\nBob\t25"
        md = tsv_to_markdown(tsv)
        self.assertIn("| Name", md)
        self.assertIn("| Alice", md)
        self.assertIn("---", md)
        back = markdown_to_tsv(md)
        self.assertEqual(back.splitlines()[0], "Name\tAge")
        self.assertIn("Alice\t30", back)
        self.assertIn("Bob\t25", back)

    def test_md_with_pipes_in_cell(self) -> None:
        md = "| a | b\\|c |\n| --- | --- |\n| 1 | 2 |"
        tsv = markdown_to_tsv(md)
        self.assertEqual(tsv.splitlines()[0], "a\tb|c")

    def test_single_header_row(self) -> None:
        tsv = "Col1\tCol2"
        md = tsv_to_markdown(tsv)
        self.assertIn("---", md)
        lines = [ln for ln in md.splitlines() if ln.strip()]
        self.assertEqual(len(lines), 2)

    def test_auto(self) -> None:
        tsv = "x\ty\n1\t2"
        out, src, dst = auto_convert(tsv)
        self.assertEqual(src, FormatKind.TSV)
        self.assertEqual(dst, FormatKind.MARKDOWN)
        self.assertIn("|", out)

        out2, src2, dst2 = auto_convert(out)
        self.assertEqual(src2, FormatKind.MARKDOWN)
        self.assertEqual(dst2, FormatKind.TSV)
        self.assertIn("\t", out2)

    def test_csv_to_markdown(self) -> None:
        csv_text = "a,b\n1,2"
        md = to_markdown(csv_text)
        self.assertIn("| a ", md)
        self.assertIn("| 1 ", md)

    def test_markdown_to_csv(self) -> None:
        md = "| Name | Note |\n| --- | --- |\n| Alice | hello, world |\n| Bob | ok |"
        out = to_csv(md)
        lines = out.splitlines()
        self.assertEqual(lines[0], "Name,Note")
        # カンマを含むセルはクォートされる
        self.assertEqual(lines[1], 'Alice,"hello, world"')
        self.assertEqual(lines[2], "Bob,ok")

    def test_tsv_to_csv(self) -> None:
        tsv = "a\tb\n1\t2"
        self.assertEqual(to_csv(tsv), "a,b\n1,2")

    def test_csv_to_tsv(self) -> None:
        csv_text = 'a,b\n"x,y",2'
        self.assertEqual(to_tsv(csv_text), "a\tb\nx,y\t2")

    def test_csv_roundtrip_quotes(self) -> None:
        rows_src = 'Name,City\n"Doe, John","New York"'
        md = to_markdown(rows_src)
        back = to_csv(md)
        self.assertIn("Doe, John", back)
        self.assertIn("New York", back)

    def test_auto_csv_to_md(self) -> None:
        out, src, dst = auto_convert("a,b\n1,2")
        self.assertEqual(src, FormatKind.CSV)
        self.assertEqual(dst, FormatKind.MARKDOWN)
        self.assertIn("|", out)


if __name__ == "__main__":
    unittest.main()
