"""Merge adjacent page continuations without crossing document or section boundaries."""
import re
from collections import defaultdict

from app.rag.models import ContentBlock
from app.rag.processing.structure_recovery import body_size, entity_anchor, heading_hint, topic_hint

PAGE_NUMBER = re.compile(r"^(?:page\s+\d+(?:\s*(?:of|/)\s*\d+)?|第?\s*\d+\s*页(?:\s*[/共]\s*\d+\s*页?)?|\d+\s*/\s*\d+|[-–—]?\s*\d+\s*[-–—]?)$", re.I)
CONTINUED = re.compile(r"\s*(?:[（(](?:continued|cont\.?|续|续表)[）)]|continued|续表?)\s*$", re.I)


def normalized(text):
    return " ".join(str(text).casefold().split())


def title(text):
    return normalized(CONTINUED.sub("", text or ""))


def join_sentence(left, right):
    left, right = left.rstrip(), right.lstrip()
    if re.search(r"[a-zA-Z]-$", left) and re.match(r"[a-z]", right):
        return left[:-1] + right
    separator = "" if re.search(r"[\u3400-\u9fff，；：、]$", left) and re.match(r"[\u3400-\u9fff]", right) else " "
    return left + separator + right


class CrossPageMerger:
    def merge(self, blocks: list[ContentBlock]) -> list[ContentBlock]:
        typical = body_size(blocks)
        clean = self._remove_noise(blocks, typical)
        merged, aliases = [], {}
        for source in clean:
            block = source.model_copy(deep=True)
            for old, new in aliases.items():
                if tuple(block.section_path[:len(old)]) == old:
                    block.section_path = [*new, *block.section_path[len(old):]]
                    break
            previous = merged[-1] if merged else None
            if (previous and block.block_type == "heading" and CONTINUED.search(block.text)
                    and previous.document_id == block.document_id and previous.section_path
                    and block.page_number == (previous.page_end or previous.page_number or 0) + 1
                    and title(block.text) == title(previous.section_path[-1])):
                aliases[tuple(block.section_path)] = tuple(previous.section_path)
                continue
            reason, rows = None, None
            if (previous and previous.document_id == block.document_id
                    and previous.section_path == block.section_path
                    and previous.page_number is not None
                    and block.page_number == (previous.page_end or previous.page_number) + 1
                    and not heading_hint(previous, typical) and not heading_hint(block, typical)):
                if previous.block_type == block.block_type == "table":
                    rows = self._table_rows(previous, block)
                    if rows is not None:
                        reason = "table_continuation"
                elif previous.block_type == block.block_type == "list" and self._same_list(previous, block):
                    reason = "list_sequence"
                elif (previous.block_type in {"paragraph", "list"} and block.block_type == "paragraph"
                      and self._continues(previous, block)):
                    reason = "paragraph_continuation"
            if reason is None:
                merged.append(block)
                continue
            if rows is not None:
                previous.table_data = rows
                previous.caption = previous.caption or block.caption
                previous.text = "\n\n".join(filter(None, [previous.caption, *(
                    "\n".join(f"{key}: {value}" for key, value in row.items()) for row in rows)]))
            elif reason == "list_sequence":
                left = self._list_text(previous)
                previous.text = left + "\n" + self._list_text(block)
                previous.list_marker = block.list_marker
            else:
                left = self._list_text(previous) if previous.block_type == "list" else previous.text
                previous.text = join_sentence(left, block.text)
            previous.page_end = block.page_end or block.page_number
            previous.source_block_ids = list(dict.fromkeys([
                *(previous.source_block_ids or [previous.block_id]),
                *(block.source_block_ids or [block.block_id]),
            ]))
            previous.merge_reason = reason
        # Pictures may reference a source block now represented by a merged block.
        owners = {source_id: block.block_id for block in merged
                  for source_id in (block.source_block_ids or [block.block_id])}
        for block in merged:
            block.related_block_ids = list(dict.fromkeys(owners[key] for key in block.related_block_ids if key in owners))
        return merged

    def _remove_noise(self, blocks, typical):
        pages = defaultdict(list)
        for block in blocks:
            if block.page_number is not None:
                pages[(block.document_id, block.page_number)].append(block)
        edges = {block.block_id for page in pages.values() for block in (page[0], page[-1])}
        repeats = defaultdict(set)
        for block in blocks:
            if block.block_id in edges and block.block_type == "paragraph" and len(block.text) < 100:
                repeats[(block.document_id, normalized(block.text))].add(block.page_number)
        clean = []
        for block in blocks:
            if block.block_type in {"page_header", "page_footer"}:
                continue
            layout = block.layout
            margin = (layout.page_height is not None and layout.top is not None and layout.bottom is not None
                      and (layout.bottom <= layout.page_height * .1 or layout.top >= layout.page_height * .9))
            edge = block.block_id in edges or margin
            if block.block_type == "paragraph" and edge:
                text = block.text.strip()
                if PAGE_NUMBER.fullmatch(text) and (margin or text == str(block.page_number) or not text.isdecimal()):
                    continue
                if len(repeats[(block.document_id, normalized(text))]) >= 2 and (margin or not heading_hint(block, typical)):
                    continue
            clean.append(block)
        return clean

    def _continues(self, previous, current):
        left, right = previous.text.rstrip(), current.text.lstrip()
        if not left or not right or left.endswith((".", "!", "?", "。", "！", "？")):
            return False
        if entity_anchor(right) and entity_anchor(right) != entity_anchor(left):
            return False
        old_topic, new_topic = topic_hint(left), topic_hint(right)
        if old_topic and new_topic and old_topic != new_topic:
            return False
        return bool(re.match(r"[a-z\u3400-\u9fff]", right) or left.endswith((",", ":", ";", "-", "，", "：", "；", "、")))

    def _same_list(self, previous, current):
        left, right = previous.list_marker or "-", current.list_marker or "-"
        numbers = [re.fullmatch(r"[（(]?(\d+)[.)、）]?", marker) for marker in (left, right)]
        if all(numbers):
            return int(numbers[1][1]) == int(numbers[0][1]) + 1
        return not any(numbers) and left == right

    def _list_text(self, block):
        marker = block.list_marker or "-"
        return block.text if re.match(r"^(?:\d+[.)、]|[-•*])\s", block.text) else f"{marker} {block.text}"

    def _table_rows(self, previous, current):
        columns = previous.table_columns
        if not columns or not previous.table_data or not current.table_data:
            return None
        if previous.caption and current.caption and title(previous.caption) != title(current.caption):
            return None
        expected = [normalized(column) for column in columns]
        actual = [normalized(column) for column in current.table_columns]
        rows = current.table_data
        repeated_header = [normalized(value) for value in rows[0].values()] == expected
        if actual != expected and not repeated_header:
            return None
        incoming = [dict(zip(columns, row.values())) for row in rows
                    if [normalized(value) for value in row.values()] != expected]
        existing = [dict(row) for row in previous.table_data
                    if [normalized(value) for value in row.values()] != expected]
        # A blank ID at the next page can be the continuation of an interrupted rule row.
        if (existing and incoming and re.search(r"\bid\b|编号", columns[0], re.I)
                and not incoming[0][columns[0]] and existing[-1][columns[0]]):
            tail = incoming.pop(0)
            for column in columns[1:]:
                if tail[column] and tail[column] != existing[-1][column]:
                    existing[-1][column] = join_sentence(str(existing[-1][column]), str(tail[column]))
        return existing + incoming
