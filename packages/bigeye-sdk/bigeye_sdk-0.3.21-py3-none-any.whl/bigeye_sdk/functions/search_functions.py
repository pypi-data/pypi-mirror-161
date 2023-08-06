import re
from typing import List


def search(search_string: str, content: List[str]) -> List[str]:
    r: List[str] = []
    search_string = f"^{search_string.replace('*', '.+')}$"
    for s in content:
        if re.search(search_string, s):
            r.append(s)
    return r
