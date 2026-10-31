import re
from typing import List, Optional, Iterable

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
    "by", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", 
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", 
    "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me", "more", 
    "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", 
    "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", 
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", 
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", 
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text for case-insensitive keyword matching."""
    if not text:
        return []
    clean = re.sub(r"[^\w\s\.-]", " ", text.lower())
    tokens = [tok.strip() for tok in clean.split() if len(tok.strip()) > 1]
    return [t for t in tokens if t not in STOPWORDS]

def extract_pr_numbers(text: str) -> List[int]:
    """Extract Pull Request references like 'Merge pull request #123', 'PR #12', '(#12)'."""
    if not text:
        return []
    # Strip HTML details/summary blocks (such as Dependabot release notes/changelogs)
    cleaned = re.sub(r"<details(?:\s+[^>]*)?>.*?</details>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    pattern = r"(?:pull\s*request\s*#?|pr\s*#?|\(#)(\d+)\)?"
    matches = re.findall(pattern, cleaned, re.IGNORECASE)
    return sorted(list(set(int(m) for m in matches)))

def extract_issue_numbers(text: str, exclude_pr_numbers: Optional[Iterable[int]] = None) -> List[int]:
    """Extract GitHub issue references like #12, Fixes #104, excluding PR numbers and release notes."""
    if not text:
        return []
    # Strip HTML details/summary blocks (such as Dependabot third-party release notes/changelogs)
    cleaned = re.sub(r"<details(?:\s+[^>]*)?>.*?</details>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<blockquote>.*?</blockquote>", " ", cleaned, flags=re.DOTALL | re.IGNORECASE)
    # Strip PR phrases so '#123' in 'Merge pull request #123' or '(#123)' is not treated as an issue
    cleaned = re.sub(r"(?:pull\s*request\s*#?|pr\s*#?|\(#)\d+\)?", " ", cleaned, flags=re.IGNORECASE)

    pr_set = set(exclude_pr_numbers) if exclude_pr_numbers is not None else set(extract_pr_numbers(text))
    pattern = r"(?:#|issue\s*#?|ticket\s*#?)(\d+)"
    matches = re.findall(pattern, cleaned, re.IGNORECASE)
    return sorted(list(set(int(m) for m in matches if int(m) not in pr_set)))

def extract_commit_shas(text: str) -> List[str]:
    """Extract 7 to 40-character hexadecimal Git commit hashes."""
    if not text:
        return []
    pattern = r"\b[0-9a-fA-F]{7,40}\b"
    matches = re.findall(pattern, text)
    return sorted(list(set(matches)))

def extract_file_paths(text: str) -> List[str]:
    """Extract candidate file paths with common code extensions."""
    if not text:
        return []
    pattern = r"\b(?:[\w\.-]+/)*[\w\.-]+\.(?:py|js|ts|jsx|tsx|json|md|html|css|go|rs|java|cpp|c|yml|yaml|sql)\b"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return sorted(list(set(matches)))
