"""Bounded, offline native-Markdown comparison; no Google credentials or writes.

Run with python3 probes/markdown-corpus.py. Child interpreters isolate upstream
imports. The independent replayer models UTF-16 insertion/range checks and leading
list-tab removal, not the complete Docs API. See generated report for limitations.
"""
from __future__ import annotations
import dataclasses
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    dict(id='plain', md='Hello office.', text='Hello office.'),
    dict(id='paragraphs', md='Alpha\n\nBeta', text='Alpha Beta'),
    dict(id='heading', md='# Meeting\n\nNotes', text='Meeting Notes', heading='Meeting'),
    dict(id='h6', md='###### Small heading', text='Small heading', heading='Small heading'),
    dict(id='bold', md='Please **approve** today.', text='Please approve today.', bold='approve'),
    dict(id='italic', md='This is *draft* copy.', text='This is draft copy.', italic='draft'),
    dict(id='bold-italic', md='***Important***', text='Important', bold='Important', italic='Important'),
    dict(id='nested-emphasis', md='**Bold and _italic_**', text='Bold and italic', bold='Bold and italic', italic='italic'),
    dict(id='link', md='[Policy](https://example.com/policy)', text='Policy', link=['Policy','https://example.com/policy']),
    dict(id='link-parentheses', md='[Policy](https://example.com/Policy_(2026))', text='Policy', link=['Policy','https://example.com/Policy_(2026)']),
    dict(id='bold-link', md='[**Policy**](https://example.com)', text='Policy', bold='Policy', link=['Policy','https://example.com']),
    dict(id='inline-code', md='Run `x = **literal**`.', text='Run x = **literal**.', code='x = **literal**'),
    dict(id='fenced-code', md='```python\nx = 1\nprint(x)\n```', text='x = 1 print(x)', code='x = 1\nprint(x)'),
    dict(id='bullets', md='- Alpha\n- Beta', text='Alpha Beta', depths=[0,0]),
    dict(id='nested-bullets', md='- Parent\n  - Child\n- Sibling', text='Parent Child Sibling', depths=[0,1,0]),
    dict(id='numbered', md='1. Alpha\n2. Beta', text='Alpha Beta', depths=[0,0], numbered=True),
    dict(id='nested-numbered', md='1. Parent\n   1. Child\n2. Sibling', text='Parent Child Sibling', depths=[0,1,0], numbered=True),
    dict(id='list-continuation', md='- First paragraph\n\n  Continuation paragraph\n\n- Second item', text='First paragraph Continuation paragraph Second item'),
    dict(id='table', md='| Key | Value |\n| --- | --- |\n| Budget | 100 |', table=[['Key','Value'],['Budget','100']], unsupported=['workspace']),
    dict(id='table-escaped-pipe', md='| Key | Value |\n| --- | --- |\n| A\\|B | 100 |', table=[['Key','Value'],['A|B','100']], unsupported=['workspace']),
    dict(id='strike', md='~~obsolete~~ current', text='obsolete current', strike='obsolete', unsupported=['workspace']),
    dict(id='image-alt', md='![Diagram](https://example.com/a.png)', text='Diagram', link=['Diagram','https://example.com/a.png'], unsupported=['gdoc']),
    dict(id='escaped-markers', md=r'Literal \*stars\* and \[brackets\].', text='Literal *stars* and [brackets].'),
    dict(id='intraword-underscore', md='office_budget_total', text='office_budget_total'),
    dict(id='blockquote', md='> Review **carefully**', text='Review carefully', bold='carefully'),
    dict(id='horizontal-rule', md='Above\n\n---\n\nBelow', text='Above Below'),
    dict(id='emoji-heading', md='# Plan 😀\n\nNext', text='Plan 😀 Next', heading='Plan 😀'),
    dict(id='emoji-before-bold', md='😀 **approved**', text='😀 approved', bold='approved'),
    dict(id='emoji-in-bold', md='**A😀B**', text='A😀B', bold='A😀B'),
    dict(id='emoji-after-bold', md='**approved** 😀\n\nNext', text='approved 😀 Next', bold='approved'),
    dict(id='emoji-link', md='😀 [Policy](https://example.com)', text='😀 Policy', link=['Policy','https://example.com']),
    dict(id='emoji-list', md='- 😀\n- Next', text='😀 Next', depths=[0,0]),
    dict(id='emoji-code', md='```\n😀\n```\n\nNext', text='😀 Next', code='😀'),
    dict(id='combining-marks', md='Cafe\u0301 **review**', text='Cafe\u0301 review', bold='review'),
    dict(id='zwj-emoji', md='👩\u200d💻 **review**\n\nNext', text='👩\u200d💻 review Next', bold='review'),
    dict(id='astral-cjk', md='𠮷 **review**\n\nNext', text='𠮷 review Next', bold='review'),
]


def worker(choice):
    sys.path.insert(0, str(ROOT/'repos'/('gdoc' if choice=='gdoc' else 'google-workspace-mcp')))
    if choice=='gdoc':
        from gdoc.mdparse import parse_markdown, to_docs_requests
    else:
        from gdocs.docs_markdown_writer import markdown_to_docs_requests
    result = {}
    for case in CASES:
        if choice=='gdoc':
            parsed = parse_markdown(case['md'])
            result[case['id']] = {'requests':to_docs_requests(parsed,1,tab_id='probe-tab'), 'tables':[dataclasses.asdict(t) for t in parsed.tables]}
        else:
            result[case['id']] = {'requests':markdown_to_docs_requests(case['md'],tab_id='probe-tab'), 'tables':[]}
    print(json.dumps(result,ensure_ascii=False))


def norm(s):
    return ' '.join(s.split())


def replay(requests):
    # Initial blank Google Doc body: terminating newline at index 1.
    buf = '\n'.encode('utf-16-le')
    errors, styles, bullets = [], [], []
    for n, request in enumerate(requests):
        kind, op = next(iter(request.items()))
        text = buf.decode('utf-16-le',errors='replace')
        boundaries = {1}
        offset=1
        for char in text:
            offset += len(char.encode('utf-16-le'))//2
            boundaries.add(offset)
        if kind=='insertText':
            loc=op['location']; at=loc['index']
            if loc.get('tabId')!='probe-tab': errors.append(f'{n}: missing/wrong tab')
            if at not in boundaries: errors.append(f'{n}: insertion {at} not UTF-16 boundary')
            if not 1<=at<=len(buf)//2: errors.append(f'{n}: insertion outside body')
            if at!=len(buf)//2: errors.append(f'{n}: insertion {at} differs from append frontier {len(buf)//2}')
            cut=2*(at-1)
            buf=buf[:cut]+op['text'].encode('utf-16-le')+buf[cut:]
            continue
        rg=op.get('range')
        if not rg: continue
        a,b=rg['startIndex'],rg['endIndex']
        if rg.get('tabId')!='probe-tab': errors.append(f'{n}: missing/wrong tab')
        if a not in boundaries or b not in boundaries: errors.append(f'{n}: {kind} [{a},{b}) splits UTF-16 character')
        if not 1<=a<b<=1+len(buf)//2: errors.append(f'{n}: invalid {kind} [{a},{b})')
        selected=buf[2*(a-1):2*(b-1)].decode('utf-16-le',errors='replace')
        if kind=='updateTextStyle': styles.append({'text':selected,'style':op['textStyle']})
        if kind=='updateParagraphStyle': styles.append({'text':selected,'paragraph':op['paragraphStyle']})
        if kind=='createParagraphBullets':
            # Model Google's removal of leading tab characters in covered paragraphs.
            pieces=text.splitlines(keepends=True); pos=1; removals=[]
            for line in pieces:
                end=pos+len(line.encode('utf-16-le'))//2
                if pos<b and end>a:
                    depth=len(line)-len(line.lstrip('\t'))
                    bullets.append({'text':line.strip(),'depth':depth,'preset':op['bulletPreset']})
                    if depth: removals.append((pos,depth))
                pos=end
            for start,count in reversed(removals):
                cut=2*(start-1); buf=buf[:cut]+buf[cut+2*count:]
    return {'text':buf.decode('utf-16-le',errors='replace'),'range_errors':errors,'styles':styles,'bullets':bullets}


def assess(case,choice,data):
    result=replay(data['requests']); failures=list(result['range_errors'])
    if 'text' in case and norm(result['text'])!=norm(case['text']): failures.append('visible text differs')
    if 'table' in case:
        rows=[t['rows'] for t in data['tables']]
        if rows!=[case['table']]: failures.append('native table cells differ/missing')
    for wanted,field in [('bold','bold'),('italic','italic'),('strike','strikethrough'),('code','weightedFontFamily')]:
        if wanted in case:
            selected=('\n' if wanted=='code' else '').join(s['text'] for s in result['styles'] if s.get('style',{}).get(field))
            if norm(selected)!=norm(case[wanted]): failures.append(f'{wanted} target differs')
    if 'heading' in case and not any(norm(s['text'])==case['heading'] and s.get('paragraph',{}).get('namedStyleType','').startswith('HEADING') for s in result['styles']): failures.append('heading range differs')
    if 'link' in case:
        links=[[s['text'],s['style']['link']['url']] for s in result['styles'] if s.get('style',{}).get('link')]
        if links != [case['link']]: failures.append('link label/URL differs')
    if 'depths' in case and [b['depth'] for b in result['bullets']] != case['depths']: failures.append('list nesting differs')
    if case.get('numbered') and not all(b['preset'].startswith('NUMBERED') for b in result['bullets']): failures.append('list numbering preset differs')
    status='unsupported-route' if choice in case.get('unsupported',[]) else ('difference' if failures else 'pass')
    return dict(status=status,findings=failures,nesting_scope='leading-tab request intent only; not final Google nesting' if any(case.get('depths',[])) else None,**result,**data)


def main():
    # Independent observer checks: a non-BMP char occupies two units, and
    # a range ending inside it must be rejected. No upstream helper involved.
    insert={'insertText':{'location':{'index':1,'tabId':'probe-tab'},'text':'😀X'}}
    good={'updateTextStyle':{'range':{'startIndex':3,'endIndex':4,'tabId':'probe-tab'},'textStyle':{'bold':True}}}
    bad={'updateTextStyle':{'range':{'startIndex':1,'endIndex':2,'tabId':'probe-tab'},'textStyle':{'bold':True}}}
    assert replay([insert,good])['styles'][0]['text']=='X'
    assert not replay([insert,good])['range_errors']
    assert replay([insert,bad])['range_errors']
    outputs={} 
    for choice,repo in [('gdoc','gdoc'),('workspace','google-workspace-mcp')]:
        proc=subprocess.run([str(ROOT/'repos'/repo/'.venv/bin/python'),str(Path(__file__).resolve()),'--worker',choice],check=True,text=True,capture_output=True)
        outputs[choice]=json.loads(proc.stdout)
    rows=[]
    for case in CASES:
        rows.append(dict(case=case,**{choice:assess(case,choice,outputs[choice][case['id']]) for choice in outputs}))
    out=ROOT/'evidence/markdown-corpus.json'
    out.write_text(json.dumps({'method':'Independent bounded UTF-16 request replay; explicit semantic expectations; no Google API', 'cases':rows},ensure_ascii=False,indent=2)+'\n')
    lines=['# Offline native Markdown corpus','',f'{len(CASES)} hand-specified specimens, two pinned upstream converters. A pass means the selected assertions passed, not full rendering fidelity. No Google API calls.','',
           'gdoc 0.21.0 (`dbfa4c3`) passed the selected assertions in 32 specimens, differed in 3, and had 1 unsupported parser-route specimen. Workspace 1.26.0 (`54b1c56`) passed 21, differed in 12, and had 3 documented unsupported specimens. This deliberately adversarial corpus is not a representative frequency sample; do not turn these counts into an overall quality score.','',
           'Three gdoc differences are concrete: a URL ending `Policy_(2026)` is truncated to `Policy_(2026` and leaves a visible closing parenthesis; `office_budget_total` becomes `officebudgettotal` with an italic middle; an escaped pipe in table cell `A\\|B` produces cells `A\\` and `B`, discarding the intended value `100`. Workspace handles the first two as expected; its native Markdown route does not support tables.','',
           'Workspace loses nested list depth, drops the second paragraph inside a list item, and miscalculates UTF-16 positions across nine specimens containing non-BMP characters. gdoc passes these selected assertions. gdoc retaining list continuation text does not certify that it remains semantically attached to the same native list item; that relationship is outside this observer.','',
           '**Live cross-check changes the nesting conclusion:** the two-space `nested-bullets` fixture already used here emits one tab in gdoc, but the later [live native snapshot](live-feature-checks.json) shows the child flattened in BOTH tools. A [direct grouped-bullet Google reference](live-followups.json) subsequently preserved child nestingLevel1. This observer counts intended leading-tab nesting; it does not reproduce all Google bullet/list behavior. Therefore its gdoc nesting pass is a request-intent check, not proof that nested lists render correctly. [Complete writer cross-check](nested-list-crosscheck.md).','',
           'Sources: [gdoc native parser](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py), [Workspace native converter](https://github.com/taylorwilsdon/google_workspace_mcp/blob/54b1c56f7f9912ce32681460d7ca38f9c2a37564/gdocs/docs_markdown_writer.py).','',
           '| Specimen | gdoc | Workspace | Difference detected |','|---|---|---|---|']
    for row in rows:
        details='; '.join(choice+': '+', '.join(row[choice]['findings']) for choice in outputs if row[choice]['findings'])
        gdoc_status=row['gdoc']['status'] + (' (request intent only)' if row['gdoc'].get('nesting_scope') else '')
        lines.append(f"| {row['case']['id']} | {gdoc_status} | {row['workspace']['status']} | {details or '—'} |")
    lines.extend(['','## Scope and interpretation','',
        'The probe calls gdoc `parse_markdown` + `to_docs_requests` (native edit/tab path) and Workspace `markdown_to_docs_requests` (populate-from-Markdown path). It does not compare either app’s separate Drive HTML/Markdown import route. gdoc native tables require later insertion phases; here their parsed row/cell data is checked, not live table construction. Image rendering is outside this gdoc parser’s native-image contract; Workspace intentionally produces linked alt text. Workspace explicitly excludes GFM tables/strikethrough, so those rows are unsupported-route, not implementation failures.','',
        'The independent request replayer starts from a blank body, uses UTF-16 bytes for insertion and style ranges, validates character boundaries and tab targeting, checks that these sequential emitters append at the correct UTF-16 frontier, and models removal of leading list tabs by createParagraphBullets. It records the text targeted when each style request executes. It does not implement Google’s full paragraph-style inheritance, tables, final style coalescing, numbering continuation, or backend sanitization. Range errors are request-level findings, not a claim Google returned a particular HTTP response.','',
        'Text comparison normalizes whitespace to avoid classifying intentional blank spacer paragraphs as bugs; consequently it does not certify exact paragraph spacing, line breaks, or code indentation. Nesting is checked independently via leading-tab removal. Style assertions name explicit expected selected text; they are not derived from either parser. No percentage score should be interpreted as real-world failure probability. Common Markdown link/underscore/list semantics are expectations of this corpus, not a claim gdoc promises complete CommonMark compliance.','',
        'Reproduce: `python3 probes/markdown-corpus.py`. Full Markdown inputs, native requests, replayed text, target ranges and findings are in [markdown-corpus.json](markdown-corpus.json).'])
    (ROOT/'evidence/markdown-corpus.md').write_text('\n'.join(lines)+'\n')
    for choice in outputs:
        print(choice,{status:sum(r[choice]['status']==status for r in rows) for status in ['pass','difference','unsupported-route']})

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--worker': worker(sys.argv[2])
    else: main()
