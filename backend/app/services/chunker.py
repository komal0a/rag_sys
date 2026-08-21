from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:

    if not text:
        return []

    words = text.split()

    chunks = []
    current_words = []
    current_length = 0

    i = 0

    while i < len(words):

        word = words[i]
        word_length = len(word) + (1 if current_words else 0)

        if current_length + word_length <= chunk_size:
            current_words.append(word)
            current_length += word_length
            i += 1

        else:
            # Save current chunk
            chunks.append(" ".join(current_words))

            # Calculate overlap based on characters
            overlap_words = []
            overlap_length = 0

            for w in reversed(current_words):
                extra = len(w) + (1 if overlap_words else 0)

                if overlap_length + extra > overlap:
                    break

                overlap_words.insert(0, w)
                overlap_length += extra

            current_words = overlap_words
            current_length = overlap_length

    # Add final chunk
    if current_words:
        final_chunk = " ".join(current_words)

        # Don't create a duplicate final chunk
        if not chunks or final_chunk != chunks[-1]:
            chunks.append(final_chunk)

    return chunks