import os
from pathlib import Path
from aiogram.types import Document
from aiogram import Bot
from uuid import uuid4
import fitz
import docx
import nbformat

SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.ipynb', '.py', '.cpp', '.cs', '.txt'}

async def download_file(bot: Bot, document: Document, download_dir: str = "downloads") -> Path:
    """
    Скачивает файл от пользователя и сохраняет в указанную папку.
    """
    os.makedirs(download_dir, exist_ok=True)
    ext = Path(document.file_name).suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Файл {document.file_name} имеет неподдерживаемый тип: {ext}")

    unique_filename = f"{uuid4().hex}{ext}"
    file_path = Path(download_dir) / unique_filename

    file = await bot.get_file(document.file_id)
    await bot.download_file(file.file_path, destination=file_path)

    return file_path

def extract_text_from_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".ipynb":
        return extract_text_from_ipynb(file_path)
    elif ext in {".py", ".cpp", ".cs", ".txt"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    else:
        raise ValueError(f"Неподдерживаемый тип файла: {ext}")

def extract_text_from_pdf(file_path: Path) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path: Path) -> str:
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_ipynb(file_path: Path) -> str:
    with open(file_path, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    md_cells = [cell['source'] for cell in nb.cells if cell['cell_type'] == 'markdown']
    return "\n".join(md_cells)
