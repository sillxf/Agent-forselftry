"""Recover missing structure from source layout and a small set of explicit rules."""
import re
from statistics import median

from app.rag.models import ContentBlock

NUMBERED = re.compile(r"^(\d{1,2}(?:\.\d{1,2})*)(?:[.)、]\s*|\s+)(\S.+)$")
CHINESE_NUMBERED = re.compile(r"^(?:第[一二三四五六七八九十百\d]+[章节]|[一二三四五六七八九十]+[、.])")
KEYWORD_HEADINGS = {
    "概述", "背景", "原理", "检测", "检测方法", "检测规则", "告警分析", "调查步骤", "应急响应",
    "处置建议", "修复建议", "影响范围", "风险评估", "漏洞分析", "总结", "overview", "definition",
    "detection", "response", "mitigation", "investigation", "prevention", "containment", "remediation", "conclusion",
}
TOPICS = {
    "检测与调查": ("检测", "告警", "日志", "调查", "排查", "detect", "investigat", "indicator", "failed login"),
    "处置与修复": ("处置", "隔离", "封禁", "修复", "恢复", "mitigat", "remediat", "isolate", "block", "patch"),
    "漏洞分析": ("漏洞", "利用", "cve-", "vulnerab", "exploit"),
}


def body_size(blocks: list[ContentBlock]) -> float | None:
    paragraphs = [b for b in blocks if b.block_type == "paragraph"]
    body = [b for b in paragraphs if len(b.text) >= 60] or paragraphs
    sizes = [b.layout.font_size or b.layout.line_height for b in body]
    sizes = [size for size in sizes if size]
    return median(sizes) if sizes else None


def heading_hint(block: ContentBlock, typical_size=None):
    """Return (level, confidence, reason), or leave an ambiguous paragraph alone."""
    text = block.text.strip()
    if block.block_type != "paragraph" or len(text) > 90 or not text:
        return None
    if text.endswith(("。", "！", "？", ".", "!", "?", ";", "；")):
        return None
    numbered = NUMBERED.match(text)
    if numbered:
        return numbered[1].count(".") + 1, .9, "numbering"
    if CHINESE_NUMBERED.match(text):
        return 1, .9, "numbering"
    if re.match(r"^[（(][一二三四五六七八九十]+[）)]", text):
        return 2, .9, "numbering"
    size = block.layout.font_size or block.layout.line_height
    if size and typical_size and size >= typical_size * 1.15:
        return (1 if size >= typical_size * 1.45 else 2), .9, "font_size"
    if block.layout.bold and len(text) <= 65:
        return 1, .85, "bold"
    if text.rstrip(":：").casefold() in KEYWORD_HEADINGS:
        return 1, .85, "keyword"
    if re.fullmatch(r"(?:CVE-\d{4}-\d{4,7}|T\d{4}(?:\.\d{3})?)(?:\s*[:：-]\s*[^。.!?！？]+)?", text, re.I):
        return 1, .85, "entity"
    return None


def topic_hint(text: str) -> str | None:
    lowered = text.casefold()
    scores = {topic: sum(word in lowered for word in words) for topic, words in TOPICS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] >= 2 and list(scores.values()).count(scores[best]) == 1 else None


def entity_anchor(text: str) -> str | None:
    match = re.match(r"^(CVE-\d{4}-\d{4,7}|T\d{4}(?:\.\d{3})?)(?=\s|[:：])", text.strip(), re.I)
    return match[1].upper() if match else None


class StructureRecovery:
    def recover(self, blocks: list[ContentBlock]) -> list[ContentBlock]:
        recovered = []
        stack = []
        typical = body_size(blocks)
        for source in blocks:
            block = source.model_copy(deep=True)
            if block.block_type == "heading":
                # Native section paths are authoritative; inferred children must not overwrite them.
                if block.section_path:
                    stack = [ContentBlock(document_id=block.document_id, block_type="heading", text=title,
                                          heading_level=index, structure_source="original")
                             for index, title in enumerate(block.section_path[:-1])]
                level = block.heading_level if block.heading_level is not None else len(block.section_path)
            else:
                anchor = entity_anchor(block.text)
                if anchor and len(block.text) > 90:
                    # Keep a long entity paragraph as evidence, not as a fabricated heading.
                    stack = [h for h in stack if h.structure_reason not in {"entity", "entity_anchor"}]
                    stack.append(ContentBlock(
                        document_id=block.document_id, block_type="heading", text=anchor,
                        heading_level=stack[-1].heading_level + 1 if stack else 1,
                        structure_source="inferred", structure_reason="entity_anchor", structure_confidence=.85,
                    ))
                hint = heading_hint(block, typical)
                if hint is None:
                    if stack:
                        block.section_path = [heading.text for heading in stack]
                        inferred = [heading for heading in stack if heading.structure_source == "inferred"]
                        if inferred:
                            block.structure_source = "inferred"
                            block.structure_reason = inferred[-1].structure_reason
                            block.structure_confidence = inferred[-1].structure_confidence
                    recovered.append(block)
                    continue
                level, confidence, reason = hint
                native = [heading for heading in stack if heading.structure_source == "original"]
                if native:
                    level += native[-1].heading_level
                if reason == "bold" and block.layout.indent is not None and stack:
                    indented = [h for h in stack if h.layout.indent is not None]
                    if indented and block.layout.indent > indented[-1].layout.indent + 8:
                        level = indented[-1].heading_level + 1
                    else:
                        peers = [h for h in indented if abs(h.layout.indent - block.layout.indent) <= 8]
                        if peers:
                            level = peers[-1].heading_level
                block.block_type = "heading"
                block.structure_source = "inferred"
                block.structure_reason, block.structure_confidence = reason, confidence
            while stack and stack[-1].heading_level >= level:
                stack.pop()
            block.heading_level = level
            stack.append(block)
            block.section_path = [heading.text for heading in stack]
            recovered.append(block)
        if not any(block.block_type == "heading" for block in recovered):
            self._group_topics(recovered)
        return recovered

    def _group_topics(self, blocks):
        # Require two neighbouring text paragraphs to agree before creating a topic section.
        text_blocks = [b for b in blocks if b.block_type in {"paragraph", "list"}]
        hints = [topic_hint(b.text) for b in text_blocks]
        supported = {b.block_id: hint for i, (b, hint) in enumerate(zip(text_blocks, hints))
                     if hint and ((i > 0 and hints[i - 1] == hint) or (i + 1 < len(hints) and hints[i + 1] == hint))}
        current_topic, current_entity = None, None
        for block in blocks:
            if block.block_type in {"paragraph", "list"}:
                anchor = entity_anchor(block.text)
                if anchor:
                    current_entity, current_topic = anchor, None
                elif block.block_id in supported:
                    current_topic, current_entity = supported[block.block_id], None
                elif not current_entity:
                    current_topic = None
            section = current_entity or current_topic
            if section:
                block.section_path = [section]
                block.structure_source = "inferred"
                block.structure_reason = "entity_anchor" if current_entity else "topic_keywords"
                block.structure_confidence = .85 if current_entity else .7
            else:
                block.structure_source = "unknown"
