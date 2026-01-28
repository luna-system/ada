import re
import json

def _extract_tool_use(text):
    # Mapping common AGL verbs to actual tools
    tool_map = {
        "research": "web_search",
        "lookup": "docs_lookup",
        "wiki": "wiki_lookup",
        "analysis": "agl_analysis"
    }
    valid_tools = ["web_search", "wiki_lookup", "docs_lookup", "agl_analysis"]

    pattern_agl = r'[\u26a1\u25cf]\s*([a-z_\s]+)\s*\(\s*(.*?)\s*\)'
    match = re.search(pattern_agl, text)
    if match:
        tool_name_raw = match.group(1).strip()
        tool_name = tool_name_raw.replace(" ", "")
        args_str = match.group(2).strip() if match.group(2) else ""
        
        if tool_name in tool_map:
            tool_name = tool_map[tool_name]
            
        if tool_name in valid_tools:
            return {'tool': tool_name, 'params': args_str}
    return None

test_text = ' \u25cf research("LFM_2.5")'
result = _extract_tool_use(test_text)
print(f"Test 1: {result}")

test_text_2 = ' \u26a1 docs_lookup ("query")'
result_2 = _extract_tool_use(test_text_2)
print(f"Test 2: {result_2}")
