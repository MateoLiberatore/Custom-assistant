import re

def clean_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = re.sub(r'\s+', '_', name)
    name = name[:50]
    return name

def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    pattern = re.compile(r'```(\w+)?\s*\n(.*?)\n```', re.DOTALL)
    
    parts = []
    last_end = 0

    for match in pattern.finditer(text):
        plain_text = text[last_end:match.start()].strip()
        if plain_text:
            parts.append(("text", plain_text))
        
        lang = match.group(1) or 'text'
        code = match.group(2)
        parts.append(("code", code.strip() + "\n", lang))
        
        last_end = match.end()

    plain_text_remaining = text[last_end:].strip()
    if plain_text_remaining:
        parts.append(("text", plain_text_remaining))
    
    return parts