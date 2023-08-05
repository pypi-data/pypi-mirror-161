from typing import Optional
import re

def split_lines(string:str, comment_string:Optional[str]="#", remove_blank:bool=True,
                with_line_number:bool=False):
    lines = string.splitlines(True)
    # remove comments
    lines = [l.split(comment_string)[0] for l in lines]
    # remove blank lines
    if with_line_number:
        if remove_blank:
            return [(l, i+1) for i, l in enumerate(lines) if not re.match(r'^\s*$', l)]
        return [(l, i+1) for i, l in enumerate(lines)]
    if remove_blank:
        lines = filter(lambda x: not re.match(r'^\s*$', x), lines)
    return lines


def split_str(string:str, strip:bool=True, remove_empty:bool=False):
    if strip:
        tokens = [s.strip() for s in string.strip().split()]
    else:
        tokens = string.split()
    if remove_empty:
        # remove empty tokens
        tokens = [s for s in tokens if s]
    return tokens