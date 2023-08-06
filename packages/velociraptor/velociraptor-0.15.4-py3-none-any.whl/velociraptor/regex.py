"""
Caching functions for regexes.
"""

from functools import lru_cache
import re


@lru_cache(64)
def cached_regex(regex_match_string: str, flags: int = 0):
    return re.compile(regex_match_string, flags)
