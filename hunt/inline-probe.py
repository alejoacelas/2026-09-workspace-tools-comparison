"""Offline CommonMark inline edge cases through both pinned native writers.

Reuses the comparison's UTF-16 request observer. Expected inline text/style is
independently obtained from markdown-it CommonMark tokens; output differences
are candidates within gdoc's advertised inline-code/link/emphasis features,
not a claim that its lightweight parser promises all of CommonMark.
No credentials or Google API calls.
"""
import importlib.util
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'repos/gdoc'),str(ROOT/'repos/google-workspace-mcp')]
from gdoc.mdparse import parse_markdown,to_docs_requests
from gdocs.docs_markdown_writer import markdown_to_docs_requests
from markdown_it import MarkdownIt
spec=importlib.util.spec_from_file_location('corpus',ROOT/'probes/markdown-corpus.py')
corpus=importlib.util.module_from_spec(spec);spec.loader.exec_module(corpus)
CASES=[
 ('plain_link','Read [Policy](https://example.com/policy).','control'),
 ('link_title','Read [Policy](https://example.com/policy "Policy handbook").','link destinations'),
 ('link_angle','Read [Policy](<https://example.com/policy>).','link destinations'),
 ('link_empty','Keep [draft]().','empty destinations'),
 ('link_nested_label','Read [policy [draft]](https://example.com/policy).','nested link label'),
 ('link_escaped_label',r'Read [policy \[draft\]](https://example.com/policy).','control'),
 ('link_entity_query','[Search](https://example.com/?q=budget&amp;year=2026)','character references'),
 ('link_entity_label','[R&amp;D](https://example.com/research)','character references'),
 ('double_backtick','Use ``a`b`` now.','code delimiter length'),
 ('triple_backtick','Use ```a``b``` now.','code delimiter length'),
 ('code_trailing_slash',r'Use `C:\temp\` now.','backslash inside code'),
 ('code_escaped_tick',r'Use `a\`b` now.','backslash inside code'),
 ('code_trim_spaces','Use ` code ` now.','code whitespace'),
 ('code_preserve_spaces','Use `  ` now.','control'),
 ('code_literal_escape',r'Use `a\*b` now.','control'),
 ('code_entity','Use `&amp;` now.','control'),
 ('bold_contains_code_marker','**Use `a**b` today**','delimiter inside code'),
 ('italic_contains_code_marker','*Use `a*b` today*','delimiter inside code'),
 ('link_code_bracket','Read [`a]b`](https://example.com/policy).','delimiter inside code'),
 ('bold_link_title','**[Policy](https://example.com/policy "Guide")**','link destinations'),
 ('inline_entity','R&amp;D &copy; 2026 &#35;1','character references'),
 ('escaped_ampersand',r'R\&amp;D','control'),
 ('code_bold_literal','Use `**plain**` today.','control'),
 ('link_angle_space','[Policy](<https://example.com/policy draft>)','link destinations'),
]

def reference(md):
 tokens=MarkdownIt('commonmark').parse(md)
 inline=next(t for t in tokens if t.type=='inline')
 text='';styles=[];stack=[]
 for t in inline.children:
  if t.type in ('text','code_inline','html_inline'):
   start=len(text);text+=t.content
   if t.type=='code_inline':styles.append({'text':t.content,'kind':'code'})
  elif t.type in ('softbreak','hardbreak'):text+='\n'
  elif t.type in ('strong_open','em_open','link_open'):
   stack.append((t.type,len(text),t.attrGet('href')))
  elif t.type in ('strong_close','em_close','link_close'):
   typ,start,url=stack.pop();entry={'text':text[start:],'kind':{'strong_open':'bold','em_open':'italic','link_open':'link'}[typ]}
   if url is not None:entry['url']=url
   styles.append(entry)
 return {'text':text,'styles':sorted(styles,key=lambda x:json.dumps(x,sort_keys=True))}

def observe(requests):
 replay=corpus.replay(requests);styles=[]
 for s in replay['styles']:
  st=s.get('style',{})
  for key,kind in [('bold','bold'),('italic','italic'),('weightedFontFamily','code'),('link','link')]:
   if st.get(key):
    entry={'text':s['text'],'kind':kind}
    if key=='link':entry['url']=st[key]['url']
    styles.append(entry)
 return {'text':replay['text'].rstrip('\n'),'styles':sorted(styles,key=lambda x:json.dumps(x,sort_keys=True)),'range_errors':replay['range_errors']}

rows=[]
for name,md,family in CASES:
 expected=reference(md);g=parse_markdown(md)
 row={'id':name,'markdown':md,'family':family,'expected':expected}
 for tool,requests in [('gdoc',to_docs_requests(g,1,tab_id='probe-tab')),('workspace',markdown_to_docs_requests(md,tab_id='probe-tab'))]:
  actual=observe(requests);diff=[]
  if actual['text']!=expected['text']:diff.append('visible text')
  if actual['styles']!=expected['styles']:diff.append('style target or URL')
  if actual['range_errors']:diff.append('range error')
  row[tool]={'differences':diff,'actual':actual,'requests':requests}
 rows.append(row)
output={'pins':{'gdoc':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','workspace':'54b1c56f7f9912ce32681460d7ca38f9c2a37564'},'oracle':'markdown-it CommonMark token text/styles, independent of gdoc; Workspace uses this same parser so Workspace agreement is not an independent vote','cases':rows}
(ROOT/'hunt/inline-results.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
for r in rows:print(r['id'], 'gdoc='+str(r['gdoc']['differences']), 'workspace='+str(r['workspace']['differences']))
