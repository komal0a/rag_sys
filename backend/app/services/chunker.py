from typing import List


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Chunk text into a list of strings with given character chunk_size and overlap.

    This implementation preserves word boundaries and approximates overlap by words.
    """
    if not text:
        return []
    words = text.split()
    chunks = []
    i = 0
    # approximate average chars per word to compute overlap in words
    avg_word_len = 5
    overlap_words = max(0, overlap // avg_word_len)

    while i < len(words):
        chunk_words = []
        cur_len = 0
        j = i
        while j < len(words):
            w = words[j]
            if cur_len + len(w) + (1 if cur_len else 0) > chunk_size:
                break
            chunk_words.append(w)
            cur_len += len(w) + (1 if cur_len else 0)
            j += 1
        if not chunk_words:
            # single long word; force at least one word
            chunk_words.append(words[j])
            j += 1
        chunks.append(" ".join(chunk_words))
        # move i forward with overlap (start next chunk before j)
        if overlap_words > 0:
            i = max(j - overlap_words, i + 1)
        else:
            i = j
    return chunks
