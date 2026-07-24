#!/usr/bin/env python3
"""Safely inventory ZIPs/folders and extract invoice text for resumable batches."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import mimetypes
import os
import shutil
import stat
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from defusedxml import ElementTree as SafeElementTree
except ImportError:  # pragma: no cover - guarded fallback
    SafeElementTree = None

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - optional image normalization
    Image = None
    ImageOps = None


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".tif": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".webp": "image",
    ".xml": "xml",
    ".txt": "text",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepara de forma segura un lote de facturas para clasificación."
    )
    parser.add_argument("input", type=Path, help="ZIP, carpeta o factura individual.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--ocr", choices=("auto", "always", "never"), default="auto"
    )
    parser.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--max-entries", type=int, default=10000)
    parser.add_argument("--max-file-mb", type=int, default=100)
    parser.add_argument("--max-total-mb", type=int, default=2048)
    parser.add_argument("--nested-zip-depth", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--privacy-mode",
        choices=("local-only",),
        default="local-only",
        help="Impide cualquier dependencia de red; actualmente es el único modo.",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_member_path(name: str) -> Path:
    if "\x00" in name:
        raise ValueError("nombre ZIP con byte nulo")
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"ruta ZIP insegura: {name!r}")
    clean_parts = [part for part in pure.parts if part not in ("", ".")]
    if not clean_parts:
        raise ValueError(f"ruta ZIP vacía: {name!r}")
    return Path(*clean_parts)


def safe_extract_zip(
    archive: Path,
    destination: Path,
    max_entries: int,
    max_file_bytes: int,
    max_total_bytes: int,
) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    total = 0
    with zipfile.ZipFile(archive) as bundle:
        infos = bundle.infolist()
        if len(infos) > max_entries:
            raise ValueError(
                f"{archive.name}: {len(infos)} entradas exceden el límite {max_entries}"
            )
        for info in infos:
            relative = safe_member_path(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"{archive.name}: enlace simbólico no permitido: {info.filename}")
            if info.file_size > max_file_bytes:
                raise ValueError(
                    f"{archive.name}: {info.filename} excede el límite por archivo"
                )
            total += info.file_size
            if total > max_total_bytes:
                raise ValueError(f"{archive.name}: tamaño descomprimido total excesivo")

            target = destination / relative
            resolved_parent = target.parent.resolve()
            if destination.resolve() not in (resolved_parent, *resolved_parent.parents):
                raise ValueError(f"{archive.name}: salida fuera del destino")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            extracted.append(target)
    return extracted


def expand_nested_zips(
    root: Path,
    depth: int,
    limits: tuple[int, int, int],
) -> None:
    if depth <= 0:
        return
    archives = sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".zip"
    )
    for archive in archives:
        destination = archive.with_name(f"{archive.stem}__contenido")
        if destination.exists():
            continue
        safe_extract_zip(archive, destination, *limits)
        expand_nested_zips(destination, depth - 1, limits)


def command_version(command: str, args: list[str]) -> str | None:
    executable = shutil.which(command)
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else executable


def tesseract_language() -> str | None:
    executable = shutil.which("tesseract")
    if not executable:
        return None
    result = subprocess.run(
        [executable, "--list-langs"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=20,
    )
    languages = {line.strip() for line in result.stdout.splitlines()[1:]}
    selected = [code for code in ("spa", "eng") if code in languages]
    return "+".join(selected) if selected else None


def run_text_command(command: list[str], timeout: int = 300) -> str:
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip()[-1000:]
        raise RuntimeError(f"{' '.join(command[:2])}: {detail}")
    return result.stdout


def normalize_image(source: Path, destination: Path) -> Path:
    if Image is None or ImageOps is None:
        return source
    with Image.open(source) as image:
        normalized = ImageOps.exif_transpose(image)
        if normalized.mode not in ("L", "RGB"):
            normalized = normalized.convert("RGB")
        normalized.save(destination, format="PNG", optimize=True)
    return destination


def ocr_image(path: Path, language: str | None) -> str:
    executable = shutil.which("tesseract")
    if not executable or not language:
        raise RuntimeError("tesseract con idioma spa/eng no está disponible")
    with tempfile.TemporaryDirectory(prefix="iva-ocr-image-") as temp_name:
        normalized = normalize_image(path, Path(temp_name) / "normalized.png")
        return run_text_command(
            [
                executable,
                str(normalized),
                "stdout",
                "-l",
                language,
                "--psm",
                "6",
            ]
        )


def pdf_page_count(path: Path) -> int | None:
    executable = shutil.which("pdfinfo")
    if not executable:
        return None
    try:
        output = run_text_command([executable, str(path)], timeout=60)
    except Exception:
        return None
    for line in output.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def ocr_pdf(path: Path, language: str | None) -> str:
    pdftoppm = shutil.which("pdftoppm")
    tesseract = shutil.which("tesseract")
    if not pdftoppm or not tesseract or not language:
        raise RuntimeError("pdftoppm/tesseract con spa/eng no están disponibles")
    texts = []
    with tempfile.TemporaryDirectory(prefix="iva-ocr-pdf-") as temp_name:
        prefix = Path(temp_name) / "page"
        subprocess.run(
            [pdftoppm, "-r", "250", "-png", str(path), str(prefix)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,
            check=True,
        )
        for page in sorted(Path(temp_name).glob("page-*.png")):
            texts.append(
                run_text_command(
                    [tesseract, str(page), "stdout", "-l", language, "--psm", "6"],
                    timeout=300,
                )
            )
    return "\n\n".join(texts)


def extract_pdf(path: Path, ocr_mode: str, language: str | None) -> tuple[str, str]:
    pdftotext = shutil.which("pdftotext")
    text = ""
    method = "none"
    if pdftotext and ocr_mode != "always":
        text = run_text_command(
            [pdftotext, "-layout", "-nopgbrk", str(path), "-"],
            timeout=180,
        )
        method = "pdftotext"
    if ocr_mode == "always" or (ocr_mode == "auto" and len(text.strip()) < 80):
        text = ocr_pdf(path, language)
        method = "tesseract-pdf"
    if not text.strip():
        raise RuntimeError("no se pudo extraer texto del PDF")
    return text, method


def extract_xml(path: Path) -> str:
    raw = path.read_bytes()
    if SafeElementTree is None:
        upper = raw[:10000].upper()
        if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
            raise RuntimeError("XML con DTD/entidades rechazado")
        import xml.etree.ElementTree as element_tree

        root = element_tree.fromstring(raw)
    else:
        root = SafeElementTree.fromstring(raw)
    lines = []
    for element in root.iter():
        text = (element.text or "").strip()
        if text:
            tag = str(element.tag).rsplit("}", 1)[-1]
            lines.append(f"{tag}: {text}")
    return "\n".join(lines)


def extract_one(
    path: Path,
    kind: str,
    ocr_mode: str,
    language: str | None,
) -> dict[str, Any]:
    try:
        if kind == "pdf":
            text, method = extract_pdf(path, ocr_mode, language)
            pages = pdf_page_count(path)
        elif kind == "image":
            if ocr_mode == "never":
                raise RuntimeError("OCR desactivado para imagen")
            text, method, pages = ocr_image(path, language), "tesseract-image", 1
        elif kind == "xml":
            text, method, pages = extract_xml(path), "xml", None
        elif kind == "text":
            text, method, pages = path.read_text(
                encoding="utf-8", errors="replace"
            ), "text", None
        else:
            raise RuntimeError(f"tipo no soportado: {kind}")
        return {
            "status": "extracted",
            "method": method,
            "pages": pages,
            "characters": len(text),
            "text": text,
            "error": None,
        }
    except Exception as error:
        return {
            "status": "error",
            "method": None,
            "pages": None,
            "characters": 0,
            "text": "",
            "error": str(error),
        }


def prepare_source(
    input_path: Path,
    output: Path,
    nested_depth: int,
    limits: tuple[int, int, int],
) -> tuple[Path, list[Path], str]:
    if input_path.is_dir():
        return input_path.resolve(), [], "directory"
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if input_path.suffix.lower() == ".zip":
        originals = output / "originals"
        extracted = safe_extract_zip(input_path, originals, *limits)
        expand_nested_zips(originals, nested_depth, limits)
        return originals.resolve(), extracted, "zip"
    return input_path.parent.resolve(), [input_path.resolve()], "single_file"


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    output = args.output.resolve()
    manifest_path = output / "manifest.json"
    previous_manifest: dict[str, Any] = {}
    if manifest_path.exists() and not args.resume:
        raise FileExistsError(
            f"{manifest_path} ya existe; use --resume o un directorio nuevo"
        )
    if manifest_path.exists() and args.resume:
        try:
            previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous_manifest = {}
    output.mkdir(parents=True, exist_ok=True)
    text_dir = output / "text"
    text_dir.mkdir(exist_ok=True)

    limits = (
        args.max_entries,
        args.max_file_mb * 1024 * 1024,
        args.max_total_mb * 1024 * 1024,
    )
    source_root, explicit_files, input_kind = prepare_source(
        input_path, output, args.nested_zip_depth, limits
    )
    if explicit_files and input_kind == "single_file":
        candidates = explicit_files
    else:
        candidates = sorted(path for path in source_root.rglob("*") if path.is_file())

    output_is_inside_source = source_root in output.parents or source_root == output
    if output_is_inside_source:
        candidates = [
            path for path in candidates if output not in (path, *path.parents)
        ]

    entries: list[dict[str, Any]] = []
    ignored_entries: list[dict[str, Any]] = []
    for path in candidates:
        suffix = path.suffix.lower()
        kind = SUPPORTED_EXTENSIONS.get(suffix)
        if not kind:
            ignored_entries.append(
                {
                    "relative_path": (
                        str(path.relative_to(source_root))
                        if path.is_relative_to(source_root)
                        else path.name
                    ),
                    "extension": suffix,
                    "size_bytes": path.stat().st_size,
                    "reason": "tipo no admitido como factura",
                }
            )
            continue
        size = path.stat().st_size
        relative = (
            str(path.relative_to(source_root))
            if path.is_relative_to(source_root)
            else path.name
        )
        entries.append(
            {
                "relative_path": relative,
                "absolute_path": str(path.resolve()),
                "extension": suffix,
                "kind": kind,
                "mime_guess": mimetypes.guess_type(path.name)[0],
                "size_bytes": size,
                "sha256": sha256_file(path),
            }
        )

    by_hash: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        by_hash.setdefault(entry["sha256"], []).append(entry)

    language = tesseract_language()
    representatives = {
        digest: Path(group[0]["absolute_path"]) for digest, group in by_hash.items()
    }
    extracted_by_hash: dict[str, dict[str, Any]] = {}
    previous_by_hash = {
        item.get("sha256"): item
        for item in previous_manifest.get("files", [])
        if item.get("sha256")
    }
    pending: dict[str, Path] = {}
    for digest, path in representatives.items():
        previous = previous_by_hash.get(digest)
        previous_text = (
            output / previous["text_path"]
            if previous and previous.get("text_path")
            else None
        )
        if (
            args.resume
            and previous
            and previous.get("status") == "extracted"
            and previous_text
            and previous_text.is_file()
        ):
            text = previous_text.read_text(encoding="utf-8", errors="replace")
            extracted_by_hash[digest] = {
                "status": "extracted",
                "method": previous.get("extraction_method"),
                "pages": previous.get("pages"),
                "characters": len(text),
                "text": text,
                "error": None,
                "resumed": True,
            }
        else:
            pending[digest] = path
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        future_map = {
            pool.submit(
                extract_one,
                path,
                SUPPORTED_EXTENSIONS[path.suffix.lower()],
                args.ocr,
                language,
            ): digest
            for digest, path in pending.items()
        }
        for future in concurrent.futures.as_completed(future_map):
            digest = future_map[future]
            extracted_by_hash[digest] = future.result()

    for entry in entries:
        result = extracted_by_hash[entry["sha256"]]
        text_path = text_dir / f"{entry['sha256']}.txt"
        if result["status"] == "extracted" and (
            not text_path.exists() or not args.resume
        ):
            text_path.write_text(result["text"], encoding="utf-8")
        entry.update(
            {
                "status": result["status"],
                "extraction_method": result["method"],
                "pages": result["pages"],
                "characters": result["characters"],
                "text_path": (
                    str(text_path.relative_to(output))
                    if result["status"] == "extracted"
                    else None
                ),
                "error": result["error"],
                "duplicate_count": len(by_hash[entry["sha256"]]),
                "resumed": bool(result.get("resumed")),
            }
        )
        quality_flags = []
        if result["status"] == "extracted":
            if result["method"] in {"tesseract-pdf", "tesseract-image"}:
                quality_flags.append("revisar_ocr")
            if result["characters"] < 300:
                quality_flags.append("texto_muy_corto")
            pages = result.get("pages")
            if pages and result["characters"] / pages < 120:
                quality_flags.append("poco_texto_por_pagina")
        entry["quality_flags"] = quality_flags
        entry["needs_review"] = bool(quality_flags or result["status"] == "error")

    duplicates = [
        {
            "sha256": digest,
            "paths": [entry["relative_path"] for entry in group],
        }
        for digest, group in sorted(by_hash.items())
        if len(group) > 1
    ]
    tools = {
        "pdftotext": command_version("pdftotext", ["-v"]),
        "pdftoppm": command_version("pdftoppm", ["-v"]),
        "tesseract": command_version("tesseract", ["--version"]),
        "tesseract_language": language,
    }
    manifest = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(input_path),
        "input_kind": input_kind,
        "privacy_mode": args.privacy_mode,
        "source_root": str(source_root),
        "ocr_mode": args.ocr,
        "tools": tools,
        "summary": {
            "files": len(entries),
            "unique_files": len(by_hash),
            "duplicates": sum(len(group) - 1 for group in by_hash.values()),
            "extracted": sum(entry["status"] == "extracted" for entry in entries),
            "errors": sum(entry["status"] == "error" for entry in entries),
            "needs_review": sum(entry["needs_review"] for entry in entries),
            "ignored_files": len(ignored_entries),
        },
        "duplicate_groups": duplicates,
        "ignored_files": ignored_entries,
        "files": entries,
    }
    temporary = manifest_path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, manifest_path)
    print(json.dumps(manifest["summary"], ensure_ascii=False))
    return 0 if not manifest["summary"]["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
