def read_skill_md(file_path: str) -> str:
    with open(file_path, 'r') as f:
        content = f.read()
    return content