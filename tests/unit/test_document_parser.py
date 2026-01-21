from pathlib import Path

import pytest

from src.services import document_parser


def test_parse_document_routes_by_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    docx = tmp_path / "sample.docx"
    docx.write_text("stub")

    pdf = tmp_path / "sample.pdf"
    pdf.write_text("stub")

    xlsx = tmp_path / "sample.xlsx"
    xlsx.write_text("stub")

    monkeypatch.setattr(document_parser, "extract_docx_text", lambda _: "DOCX")
    monkeypatch.setattr(document_parser, "extract_pdf_text", lambda _: ["PDF PAGE"])
    monkeypatch.setattr(document_parser, "extract_xlsx_text", lambda _: "XLSX")

    docx_parsed = document_parser.parse_document(docx, "docx")
    assert "DOCX" in docx_parsed.text

    pdf_parsed = document_parser.parse_document(pdf, "pdf")
    assert "PDF PAGE" in pdf_parsed.text
    assert "PAGE 1" in pdf_parsed.text

    xlsx_parsed = document_parser.parse_document(xlsx, "xlsx")
    assert "XLSX" in xlsx_parsed.text


def test_extract_md_text(tmp_path: Path) -> None:
    md = tmp_path / "sample.md"
    md.write_text("# Заголовок", encoding="utf-8")
    text = document_parser.extract_md_text(md)
    assert "Заголовок" in text


def test_normalize_text_truncates() -> None:
    pages = ["A" * 120_000, "B" * 120_000]
    combined = document_parser.normalize_text(pages, max_chars=1000)
    assert combined.endswith("[Текст усечен]")
