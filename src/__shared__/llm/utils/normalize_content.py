from typing import Any

def normalize_content(content: Any):

    if content is None:
        return ""
    
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        return "".join(str(item) for item in content)

    return content