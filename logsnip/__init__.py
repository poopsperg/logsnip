"""logsnip — extract and filter structured log chunks from large files."""

__version__ = "0.1.0"
__all__ = ["extract", "filter_chunks"]


def extract(text, start_marker, end_marker):
    """Extract chunks of text between start_marker and end_marker.

    Returns a list of strings, each being the content between one
    start/end marker pair (exclusive of the markers themselves).
    """
    chunks = []
    start = 0
    while True:
        s = text.find(start_marker, start)
        if s == -1:
            break
        e = text.find(end_marker, s + len(start_marker))
        if e == -1:
            break
        chunks.append(text[s + len(start_marker):e])
        start = e + len(end_marker)
    return chunks
