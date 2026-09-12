"""Inspect UTF-16 ranges for the same synthetic Markdown in both converters."""
import json
from pathlib import Path
import sys

choice = sys.argv[1]
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'repos' / ('gdoc' if choice == 'gdoc' else 'google-workspace-mcp')))
source = '# Plan 😀\n\nNext'
if choice == 'gdoc':
    from gdoc.mdparse import parse_markdown, to_docs_requests
    requests = to_docs_requests(parse_markdown(source), 1)
else:
    from gdocs.docs_markdown_writer import markdown_to_docs_requests
    requests = markdown_to_docs_requests(source)
heading_range = next(r['updateParagraphStyle']['range'] for r in requests if 'updateParagraphStyle' in r)
expected_end = 1 + len('Plan 😀\n'.encode('utf-16-le')) // 2
assert expected_end == 9
# Characterization of the pinned snapshots, not a claim that both are correct.
assert heading_range['endIndex'] == (9 if choice == 'gdoc' else 8)
print(json.dumps({'markdown': source, 'expected_heading_end': expected_end,
                  'actual_heading_range': heading_range, 'requests': requests}, indent=2))
