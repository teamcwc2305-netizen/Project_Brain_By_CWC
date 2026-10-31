NOT_FOUND_MESSAGE = "Not found in the available project history."

def format_file_history_answer(file_path: str, count: int, most_recent_sha: str, commit_msg: str, author: str) -> str:
    return (
        f"File '{file_path}' has {count} recorded commit(s). "
        f"The most recent modification was by {author} in commit {most_recent_sha[:7]}: \"{commit_msg.strip()}\"."
    )

def format_author_files_answer(author: str, count: int, files: list) -> str:
    file_list_str = ", ".join(files[:5]) + ("..." if len(files) > 5 else "")
    return f"Developer '{author}' has modified {count} recorded file(s), including: {file_list_str}."

def format_issue_answer(issue_num: int, title: str, state: str, commits: list) -> str:
    commits_str = ", ".join([c[:7] for c in commits]) if commits else "No directly referencing commits found"
    return f"Issue #{issue_num} ('{title}') is currently {state}. Connected historical commits: {commits_str}."

def format_keyword_search_answer(query: str, count: int) -> str:
    return f"Found {count} matching project record(s) for query '{query}'."