"""Local mixed-format ingestion via Docling, preserving reading order and provenance."""
import hashlib
import json
import shutil
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.rag.models import ContentBlock, DocumentRecord, ParsedDocument
from app.rag.ingestion.layout import docx_layouts, item_layout

SUPPORTED_EXTENSIONS = frozenset({
    ".md", ".markdown", ".pdf", ".docx", ".xlsx", ".pptx", ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp",
})
IMAGE_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"})


def file_checksum(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def is_image_only_pdf(path: Path) -> bool:
    """Choose full-page OCR only when the entire PDF has no native text."""
    from pypdfium2 import PdfDocument

    with PdfDocument(path) as document:
        for page in document:
            text_page = page.get_textpage()
            has_text = text_page.count_chars() > 0
            text_page.close()
            page.close()
            if has_text:
                return False
    return True


class DoclingParser:
    def __init__(self, archive_dir=None, image_dir=None, converter=None, ocr_enabled=True):
        self.archive_dir = Path(archive_dir) if archive_dir is not None else None
        self.image_dir = Path(image_dir) if image_dir is not None else None
        self.converter = converter
        self.ocr_enabled = ocr_enabled
        self._converters = {}

    def _get_converter(self, full_page_ocr=False):
        if self.converter is not None:
            return self.converter
        if full_page_ocr not in self._converters:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import OcrMode, PdfPipelineOptions
            from docling.document_converter import DocumentConverter, ImageFormatOption, PdfFormatOption

            options = PdfPipelineOptions()
            options.do_ocr = self.ocr_enabled
            if full_page_ocr:
                options.ocr_options.mode = OcrMode.FULL_PAGE
            options.do_table_structure = True
            options.generate_picture_images = True
            # Image inputs have no text layer; OCR the whole source.
            image_options = options.model_copy(deep=True)
            image_options.ocr_options.mode = OcrMode.FULL_PAGE
            self._converters[full_page_ocr] = DocumentConverter(format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=image_options),
            })
        return self._converters[full_page_ocr]

    def parse(self, file_path: str | Path) -> ParsedDocument:
        path = Path(file_path).resolve(strict=True)
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported knowledge file: {path.name}")
        checksum = file_checksum(path)
        record = DocumentRecord(
            document_id=checksum, filename=path.name, file_type=path.suffix.lower().lstrip("."),
            source_path=str(path), checksum=checksum, version=checksum,
        )
        full_page_ocr = (self.converter is None and self.ocr_enabled
                         and path.suffix.lower() == ".pdf" and is_image_only_pdf(path))
        result = self._get_converter(full_page_ocr).convert(path)
        status = getattr(result.status, "value", result.status)
        if status != "success":
            raise ValueError(f"Docling conversion failed for {path.name}: {status}")
        doc = result.document
        blocks = []
        items = list(doc.iterate_items(traverse_pictures=True))
        source_layouts = docx_layouts(path, items)
        page_cells = {page.page_no: page.cells for page in getattr(result, "pages", [])}
        headings = []
        for item, _ in items:
            label = getattr(item.label, "value", item.label)
            text = getattr(item, "text", "") or ""
            kind = label if label in {"page_header", "page_footer"} else "paragraph"
            heading_level = None
            columns, rows, image_path = [], None, None
            caption = None
            if label in {"title", "section_header"}:
                kind = "heading"
                level = 0 if label == "title" else getattr(item, "level", 1)
                heading_level = level
                while headings and headings[-1][0] >= level:
                    headings.pop()
                headings.append((level, text))
                if record.title is None:
                    record.title = text
            elif label == "table":
                kind = "table"
                frame = item.export_to_dataframe(doc=doc).fillna("")
                # Duplicate/blank column labels must not silently overwrite table cells.
                seen = set()
                for index, column in enumerate(frame.columns):
                    name = str(column).strip() or f"Column {index + 1}"
                    base, number = name, 2
                    while name in seen:
                        name, number = f"{base} ({number})", number + 1
                    columns.append(name)
                    seen.add(name)
                rows = [dict(zip(columns, (str(v) for v in row)))
                        for row in frame.itertuples(index=False, name=None)]
                caption = item.caption_text(doc)
                text = "\n\n".join(filter(None, [caption, *(
                    "\n".join(f"{k}: {v}" for k, v in row.items()) for row in rows
                )]))
            elif label == "picture":
                kind = "image"
                caption = item.caption_text(doc)
                ocr = [getattr(ref.resolve(doc), "text", "") for ref in item.children]
                text = "\n".join(filter(None, [caption, *ocr]))
                if self.image_dir is not None:
                    image = item.get_image(doc)
                    if image is not None:
                        directory = self.image_dir / checksum
                        directory.mkdir(parents=True, exist_ok=True)
                        target = directory / f"picture-{len(blocks)}.png"
                        image.save(target)
                        image_path = str(target.resolve())
                # A placeholder is explicitly metadata, not a generated description.
                if not text:
                    text = f"[Image in {path.name}; no extracted text]"
            elif label == "list_item":
                kind = "list"
            elif label == "code":
                kind = "code"
            elif not text:
                continue
            pages = [prov.page_no for prov in getattr(item, "prov", [])]
            blocks.append(ContentBlock(
                block_id=str(uuid5(NAMESPACE_URL, f"{checksum}:{item.self_ref}")),
                document_id=checksum, block_type=kind, text=text,
                page_number=min(pages) if pages else None, page_end=max(pages) if pages else None,
                section_path=[text for _, text in headings], table_data=rows, table_columns=columns,
                image_path=image_path, caption=caption, heading_level=heading_level,
                list_marker=getattr(item, "marker", None) if kind == "list" else None,
                layout=source_layouts.get(item.self_ref) or item_layout(item, doc, page_cells),
            ))
        if path.suffix.lower() in IMAGE_EXTENSIONS:
            # Preserve the input even when the OCR backend emits no PictureItem.
            image_path = str(path)
            if self.image_dir is not None:
                directory = self.image_dir / checksum
                directory.mkdir(parents=True, exist_ok=True)
                target = directory / ("source" + path.suffix.lower())
                shutil.copyfile(path, target)
                image_path = str(target.resolve())
            blocks.insert(0, ContentBlock(
                block_id=str(uuid5(NAMESPACE_URL, checksum + ":source-image")),
                document_id=checksum, block_type="image", page_number=1, page_end=1,
                text="\n".join(b.text for b in blocks) or f"[Image in {path.name}; no extracted text]",
                image_path=image_path, caption=None, structure_source="unknown",
                related_block_ids=[block.block_id for block in blocks],
            ))
        for index, block in enumerate(blocks):
            if block.block_type == "image" and not block.related_block_ids:
                block.related_block_ids = [b.block_id for b in blocks[max(0, index - 1):index + 2]
                                           if b.block_id != block.block_id]
        parsed = ParsedDocument(document=record, blocks=blocks,
                                markdown=doc.export_to_markdown(), structured_data=doc.export_to_dict())
        if self.archive_dir is not None:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            (self.archive_dir / f"{checksum}.json").write_text(
                json.dumps(parsed.structured_data, ensure_ascii=False, indent=2), encoding="utf-8")
            (self.archive_dir / f"{checksum}.md").write_text(parsed.markdown, encoding="utf-8")
        return parsed
