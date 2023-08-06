from typing import Iterator, Tuple


def read(f) -> Iterator[Tuple[str, int]]:
    """Reads a text file an produces a stream of tuples representing the page number(s) and frame count(s)"""
    page = 1
    frame = None
    combo = False
    for line_number, line in enumerate(f.readlines()):
        for line_position, c in enumerate(line):
            if c.isspace():
                pass
            elif c == "-":
                yield f"PAGES {page}-{page+1}", frame
                page += 2
                frame = None
            elif c == "*" or c.isdigit():
                if frame is not None and not combo:
                    yield f"PAGE {page}", frame
                    page += 1
                    frame = None
                if c == "*":
                    combo = not combo
                else:
                    frame = (frame or 0) * 10 + int(c)
            else:
                raise RuntimeError(
                    f"Unexpected {c}, line {line_number}, position {line_position}"
                )
    if frame:
        yield f"PAGE {page}", frame
