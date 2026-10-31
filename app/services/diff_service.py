import re
from typing import List

class DiffParser:
    @staticmethod
    def extract_changed_files_from_diff(diff_text: str) -> List[str]:
        """Parses unified git diff and retrieves list of paths."""
        if not diff_text:
            return []
        changed_files = set()
        for line in diff_text.splitlines():
            match = re.match(r"^\+\+\+\s+b/(.*)$", line)
            if match:
                changed_files.add(match.group(1).strip())
            else:
                match_a = re.match(r"^---\s+a/(.*)$", line)
                if match_a and match_a.group(1) != "/dev/null":
                    changed_files.add(match_a.group(1).strip())
        return sorted(list(changed_files))