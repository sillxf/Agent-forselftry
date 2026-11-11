"""Token-budgeted splitting without decoding partial Unicode token sequences."""
import re


def count_tokens(tokenizer, text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_text(text: str, tokenizer, max_tokens: int, overlap_tokens: int = 0):
    if max_tokens < 1 or not 0 <= overlap_tokens < max_tokens:
        raise ValueError("Require max_tokens > overlap_tokens >= 0")
    start = 0
    while start < len(text):
        if count_tokens(tokenizer, text[start:]) <= max_tokens:
            if text[start:].strip():
                yield text[start:].strip()
            break
        low, high = start + 1, len(text)
        end = start
        while low <= high:
            mid = (low + high) // 2
            if count_tokens(tokenizer, text[start:mid]) <= max_tokens:
                end, low = mid, mid + 1
            else:
                high = mid - 1
        if end == start:
            raise ValueError("Token budget cannot fit one source character")
        # Prefer a paragraph, sentence or word boundary in the latter half.
        boundaries = list(re.finditer(r"\n\s*\n|[。！？.!?](?:\s|$)|\n|\s+", text[start:end]))
        preferred = [m.end() for m in boundaries if m.end() >= (end - start) // 2]
        if preferred:
            end = start + preferred[-1]
        piece = text[start:end].strip()
        if piece:
            yield piece
        next_start = end
        if overlap_tokens:
            low, high = start + 1, end
            while low <= high:
                mid = (low + high) // 2
                if count_tokens(tokenizer, text[mid:end]) <= overlap_tokens:
                    next_start, high = mid, mid - 1
                else:
                    low = mid + 1
        start = max(start + 1, next_start)
