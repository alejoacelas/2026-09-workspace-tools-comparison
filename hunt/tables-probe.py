"""24 invented gdoc table/fence cases, offline. Run: python3 hunt/tables-probe.py.
No private specimens, network calls, credentials, or upstream mutations.
"""
import dataclasses
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CASES=[
 dict(id='table_regular',md='| A | B |\n|---|---|\n|x|100|',rows=[['A','B'],['x','100']],family='control'),
 dict(id='empty_first_data_compact',md='|A|B|\n|---|---|\n||100|',rows=[['A','B'],['','100']],family='empty-edge-cells'),
 dict(id='empty_first_data_spaced',md='|A|B|\n|---|---|\n| |100|',rows=[['A','B'],['','100']],family='control'),
 dict(id='empty_first_header_compact',md='||B|\n|---|---|\n|x|100|',rows=[['','B'],['x','100']],family='empty-edge-cells'),
 dict(id='empty_last_header_compact',md='|A||\n|---|---|\n|x|100|',rows=[['A',''],['x','100']],family='empty-edge-cells'),
 dict(id='empty_middle_data',md='|A|B|C|\n|---|---|---|\n|x||100|',rows=[['A','B','C'],['x','','100']],family='control'),
 dict(id='empty_last_data',md='|A|B|\n|---|---|\n|x||',rows=[['A','B'],['x','']],family='control'),
 dict(id='empty_two_prefix_cells',md='|A|B|C|\n|---|---|---|\n|||100|',rows=[['A','B','C'],['','','100']],family='empty-edge-cells'),
 dict(id='one_column_empty_row',md='|A|\n|---|\n||',rows=[['A'],['']],family='empty-edge-cells'),
 dict(id='short_data_row',md='|A|B|\n|---|---|\n|x|',rows=[['A','B'],['x','']],family='control'),
 dict(id='long_data_row',md='|A|B|\n|---|---|\n|x|100|ignored|',rows=[['A','B'],['x','100']],family='control'),
 dict(id='escaped_pipe_known',md='|A|B|\n|---|---|\n|x\\|y|100|',rows=[['A','B'],['x|y','100']],family='already-reported-escaped-pipe'),
 dict(id='bold_unicode_cells',md='|A|B|\n|---|---|\n|**😀**|café|',rows=[['A','B'],['😀','café']],family='control'),
 dict(id='no_outer_pipes',md='A | B\n---|---\nx | 100',rows=[['A','B'],['x','100']],family='unsupported-grammar'),
 dict(id='mismatched_header_separator',md='|A|B|\n|---|\n|x|100|',rows=[],family='malformed-table-interpretation'),
 dict(id='fence_basic',md='```\n**literal**\n```',text='**literal**',family='control'),
 dict(id='fence_language',md='```python\nx = 2\n```',text='x = 2',family='control'),
 dict(id='fence_multiword_info',md='```python title=demo.py\n**literal**\n```',text='**literal**',family='fence-info-grammar'),
 dict(id='fence_false_close_backtick',md='```\nfirst\n```not-a-close\n**literal**\n```',text='first\n```not-a-close\n**literal**',family='fence-info-grammar'),
 dict(id='fence_false_close_tilde',md='~~~\nfirst\n~~~not-a-close\n**literal**\n~~~',text='first\n~~~not-a-close\n**literal**',family='fence-info-grammar'),
 dict(id='fence_close_trailing_spaces',md='```\nx\n```   ',text='x',family='control'),
 dict(id='fence_longer_close',md='```\nx\n````',text='x',family='control'),
 dict(id='fence_short_inner',md='````\na\n```\nb\n````',text='a\n```\nb',family='control'),
 dict(id='fence_unclosed',md='```\n**literal**',text='**literal**',family='control'),
]


def worker(app):
 if app=='reference':
  from markdown_it import MarkdownIt
  parser=MarkdownIt('commonmark').enable('table')
  sys.path.insert(0,str(ROOT/'repos/google-workspace-mcp'))
  from gdocs.docs_markdown_writer import markdown_to_docs_requests
  result={}
  for c in CASES:
   requests=markdown_to_docs_requests(c['md']) if 'text' in c else []
   inserted=''.join(r['insertText']['text'] for r in requests if 'insertText' in r)
   result[c['id']]={'html':parser.render(c['md']),'workspace_requests':requests,'workspace_literal_text_matches':inserted.rstrip('\n')==c['text'] if 'text' in c else None}
  print(json.dumps(result))
  return
 sys.path.insert(0,str(ROOT/'repos/gdoc'))
 from gdoc.mdparse import parse_markdown,parse_inline,to_docs_requests
 spec=importlib.util.spec_from_file_location('corpus',ROOT/'probes/markdown-corpus.py')
 corpus=importlib.util.module_from_spec(spec);spec.loader.exec_module(corpus)
 outputs={}
 for case in CASES:
  p=parse_markdown(case['md']);requests=to_docs_requests(p,1,tab_id='probe-tab')
  replay=corpus.replay(requests)
  outputs[case['id']]={'plain_text':p.plain_text,'tables':[dataclasses.asdict(t) for t in p.tables],
   'rendered_cells':[[[parse_inline(cell)[0] for cell in row] for row in t.rows] for t in p.tables],
   'styles':[dataclasses.asdict(s) for s in p.styles], 'requests':requests,'request_range_findings':replay['range_errors']}
 print(json.dumps(outputs,ensure_ascii=False))


def main():
 outputs={}
 for app,repo in [('gdoc','gdoc'),('reference','google-workspace-mcp')]:
  p=subprocess.run([str(ROOT/'repos'/repo/'.venv/bin/python'),str(Path(__file__).resolve()),'--worker',app],check=True,text=True,capture_output=True)
  outputs[app]=json.loads(p.stdout)
 rows=[]
 for case in CASES:
  observed=outputs['gdoc'][case['id']];failures=[]
  if 'rows' in case:
   expected=[case['rows']] if case['rows'] else []
   if observed['rendered_cells']!=expected:failures.append('table rows/cell mapping differ')
  else:
   if observed['plain_text'].rstrip('\n')!=case['text']:failures.append('literal code text differs')
   code='\n'.join(observed['plain_text'][s['start']:s['end']] for s in observed['styles'] if s['style'].get('weightedFontFamily'))
   if code!=case['text']:failures.append('code style coverage differs')
   if any(s['style'].get('bold') for s in observed['styles']):failures.append('literal Markdown acquired bold')
  failures+=observed['request_range_findings']
  status=('scope-gap' if case['family']=='unsupported-grammar' else 'excluded-malformed-table' if case['family']=='malformed-table-interpretation' else 'known-duplicate' if case['family'].startswith('already-reported') else 'candidate' if failures else 'pass')
  rows.append({'case':case,'status':status,'findings':failures,'observed':observed,'independent_reference_html':outputs['reference'][case['id']]['html'],'workspace_native_requests':outputs['reference'][case['id']]['workspace_requests'],'workspace_literal_text_matches':outputs['reference'][case['id']]['workspace_literal_text_matches']})
 assert all(r['status']=='pass' for r in rows if r['case']['family']=='control')
 (ROOT/'hunt/tables-results.json').write_text(json.dumps({'pin':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','cases':rows},ensure_ascii=False,indent=2)+'\n')
 lines=['# Native table and fenced-code bug hunt','',
 '**Two new repair families reproduced offline:** empty-edge table cells are erased or shifted; opening and closing fence information strings are parsed with the wrong grammar. These are invented specimens, not copied campaign documents.','',
 'The 24 cases run the pinned gdoc parser and native request generator. A separate markdown-it CommonMark parser with its table extension provides readable reference HTML; explicit cell/text expectations remain in the fixture definitions. This tests parser output and generated requests, not Google acceptance or final rendering.','',
 '| Case | Result | Finding |','|---|---|---|']
 for r in rows:lines.append('| '+r['case']['id']+' | '+r['status']+' | '+('; '.join(r['findings']) or 'selected assertions pass')+' |')
 lines+=['','## Candidate T1: empty edge cells move or delete data','',
 'Input `|A|B|` / `|---|---|` / `||100|` should have an empty first data cell and `100` in the second. gdoc creates `["100", ""]`. With header `||B|`, it infers one column instead of two and drops the second data value. Spaces inside the empty cell avoid this: `| |100|` passes. Empty middle/trailing data cells and short-row padding controls pass. The single-column empty row `||` is not recognized as a row at all.','',
 'Root causes are edge stripping with `line.strip("|")` before splitting and `_TABLE_ROW_RE` requiring a nonempty interior. The shared repair boundary is preserving empty-cell identity, not treating each manifestation as a separate bug. Empty-header width loss is the strongest content-loss specimen. Native route: `write --tab` / `insert` / formatted table insertion call `parse_markdown`, and `_insert_table` consumes these rows.','',
 '## Candidate T2: fence info strings expose literal code to Markdown parsing','',
 'Inside a fenced code block, the line `````not-a-close`` is literal code: a closing fence may only be followed by spaces/tabs. gdoc treats it as a closing delimiter, discards that line and then renders `**literal**` as bold prose. The same issue occurs with tilde fences. Conversely, the valid opening info string `python title=demo.py` is rejected by gdoc, leaving the opening marker visible and parsing the body as Markdown. Both arise from reusing `_FENCE_RE` with one optional nonspace token for opening and closing lines.','',
 'Workspace’s native converter retained the exact intended literal code text for all nine fence specimens, including all three gdoc failures (offline request inspection only). Simple/language fences, whitespace-only closing suffixes, longer closing delimiters, shorter internal delimiters and unterminated fences pass these assertions. The opening and closing failures need distinct regression cases but belong to one fence grammar repair.','',
 '## Exclusions and deduplication','',
 'Escaped-pipe corruption is already in the comparison corpus, so its replay is a known duplicate. Missing outer table pipes is valid GFM but absent from this parser’s recognized table grammar; recorded as a scope gap rather than a new corruption family. A mismatched header/separator column count is not a GFM table and is excluded from positive table expectations even though gdoc recognizes it.','',
 'The campaign consolidated family headings/root-cause summaries were reviewed for deduplication. Existing broad Markdown export/parser and balanced-link families overlap the area, but the reviewed report does not identify these empty-edge-cell or fenced-info subcases. This is a new concrete trigger/root-cause claim, not proof no earlier private test ever covered them. No private specimen or private report excerpt is reproduced here.','',
 '## Sources and reproduction','',
 '- [gdoc native parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L323).','- [gdoc native table insertion](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L764).','- [CommonMark fenced-code grammar](https://spec.commonmark.org/0.31.2/#fenced-code-blocks): opening info strings and closing-fence suffixes have different rules.','- [GFM table grammar](https://github.github.com/gfm/#tables-extension-): cells may be empty; optional exterior pipes and uneven body rows have defined handling.','- Run `python3 hunt/tables-probe.py`; [raw inputs, outputs and request evidence](tables-results.json).']
 (ROOT/'hunt/tables-results.md').write_text('\n'.join(lines)+'\n')
 print({s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})})

if __name__=='__main__':
 if len(sys.argv)>1:worker(sys.argv[2])
 else:main()
