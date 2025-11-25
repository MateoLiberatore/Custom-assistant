import re

def clean_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:\*\?"<>|]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name[:50]

def extract_code_blocks(text: str):
    pattern = re.compile(r'```(\w+)?\s*\n(.*?)\n```', re.DOTALL)
    parts = []
    last_end = 0
    for match in pattern.finditer(text):
        plain = text[last_end:match.start()].strip()
        if plain:
            parts.append(("text", plain))
        lang = match.group(1) or 'text'
        code = match.group(2)
        parts.append(("code", code.strip() + "\n", lang))
        last_end = match.end()
    tail = text[last_end:].strip()
    if tail:
        parts.append(("text", tail))
    return parts
