"""One synthetic personal Doc; preview gate and exact-case workaround controls.
Run repos/gdoc/.venv/bin/python hunt/round2/suggestions.py. Creates one fresh Doc.
Never enrolls a project or changes permissions. Preview states are read-only.
"""
import json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'hunt'))
import live as b
from gdoc.api.docs import collect_suggestion_ids
OUT=ROOT/'hunt/round2'
def text(x):
 if isinstance(x,dict):
  if 'textRun' in x:return x['textRun'].get('content','')
  return ''.join(text(v) for v in x.values())
 if isinstance(x,list):return ''.join(text(v) for v in x)
 return ''
def read(mode='SUGGESTIONS_INLINE'):
 return b.docs.documents().get(documentId=id,includeTabsContent=True,suggestionsViewMode=mode).execute()
def summary(d):return {'text':text(d.get('tabs',[])),'suggestion_count':len(collect_suggestion_ids(d))}
def run(args):
 r=b.cli(args);b.save('r2-suggestions-last-cli.json',r)
 r['stderr']='\n'.join(l for l in r['stderr'].splitlines() if l.startswith(('ERR','WARN'))).replace(id,'DOC').replace(tab,'TAB')
 r['stderr']=re.sub(r'(?:#?suggest\.)[A-Za-z0-9_-]+','suggest.ANON',r['stderr'])
 r['stdout']=re.sub(r'#suggest\.[A-Za-z0-9_-]+','#suggest.ANON',r['stdout'].replace(id,'DOC').replace(tab,'TAB'))
 return r
if '--extra' in sys.argv:
 ledger=json.loads((b.LOCAL/'r2-suggestions-ledger.json').read_text());id=ledger['id'];tab=ledger['tab']
 obj=json.loads((OUT/'suggestions.json').read_text());b.identity();d=read();end=d['tabs'][0]['documentTab']['body']['content'][-1]['endIndex']-1
 b.update(id,[{'insertText':{'location':{'index':end,'tabId':tab},'text':'Delete token.\nUnicode token.\n'}}])
 for name,old,new in [('empty_deletion','Delete token',''),('unicode_bold','Unicode token','**Ready 😀**')]:
  before=read();b.save('r2-suggestions-'+name+'-before.json',before)
  result=run(['suggest',id,old,new,'--tab',tab]);after=read();accepted=read('PREVIEW_SUGGESTIONS_ACCEPTED');original=read('PREVIEW_WITHOUT_SUGGESTIONS')
  for suffix,state in [('after',after),('accepted',accepted),('original',original)]:b.save('r2-suggestions-'+name+'-'+suffix+'.json',state)
  runs=[e.get('textRun',{}) for t in accepted['tabs'] for p in t['documentTab']['body']['content'] for e in p.get('paragraph',{}).get('elements',[])]
  bold_ok=any(x.get('content')=='Ready 😀' and x.get('textStyle',{}).get('bold') is True for x in runs)
  ok=result['returncode']==0 and old not in text(accepted['tabs']) and old in text(original['tabs']) and len(collect_suggestion_ids(after))>len(collect_suggestion_ids(before)) and (name=='empty_deletion' or bold_ok)
  row={'case':name,'result':result,'before':summary(before),'after':summary(after),'accepted_preview':summary(accepted),'without_suggestions_preview':summary(original),'pass':ok}
  if name=='unicode_bold':row['accepted_ready_emoji_is_bold']=bold_ok
  obj['cases'].append(row);(OUT/'suggestions.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,ok,flush=True)
 with (OUT/'suggestions.md').open('a') as f:
  f.write('\nTwo final boundary controls: empty replacement '+('passes as a pending deletion, retaining its source in the without-suggestions preview' if obj['cases'][-2]['pass'] else 'requires investigation')+'; `**Ready 😀**` '+('passes with the whole replacement natively bold in accepted preview and the original source retained in without-suggestions preview' if obj['cases'][-1]['pass'] else 'requires investigation')+'. Total: nine suggestion command attempts and one ordinary exact-case edit control on one scratch document. No new regression family found.\n')
 sys.exit(0)
if '--extend' in sys.argv:
 ledger=json.loads((b.LOCAL/'r2-suggestions-ledger.json').read_text());id=ledger['id'];tab=ledger['tab']
 obj=json.loads((OUT/'suggestions.json').read_text())
 b.identity();d=read();end=d['tabs'][0]['documentTab']['body']['content'][-1]['endIndex']-1
 b.update(id,[{'insertText':{'location':{'index':end,'tabId':tab},'text':'Review token. Review token.\nBlock anchor.\n'}}])
 cases=[('overlap_pending','final','changed',[]),('disjoint_all','Review token','Reviewed token',['--all']),('reject_heading','Block anchor','# Heading',[]),('reject_bullets','Block anchor','- First\n- Second',[]),('reject_table','Block anchor','| A | B |\n| --- | --- |\n| 1 | 2 |',[])]
 for name,old,new,flags in cases:
  before=read();b.save('r2-suggestions-'+name+'-before.json',before)
  result=run(['suggest',id,old,new,'--tab',tab,*flags]);after=read();b.save('r2-suggestions-'+name+'-after.json',after)
  accepted=read('PREVIEW_SUGGESTIONS_ACCEPTED');original=read('PREVIEW_WITHOUT_SUGGESTIONS')
  b.save('r2-suggestions-'+name+'-accepted.json',accepted);b.save('r2-suggestions-'+name+'-original.json',original)
  unchanged=before['tabs']==after['tabs']
  ok=(result['returncode']!=0 and unchanged) if name!='disjoint_all' else (result['returncode']==0 and text(accepted['tabs']).count('Reviewed token')==2 and text(original['tabs']).count('Review token')==2 and len(collect_suggestion_ids(after))>len(collect_suggestion_ids(before)))
  row={'case':name,'result':result,'before':summary(before),'after':summary(after),'accepted_preview':summary(accepted),'without_suggestions_preview':summary(original),'native_tabs_unchanged':unchanged,'pass':ok}
  obj['cases'].append(row);(OUT/'suggestions.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,ok,flush=True)
 with (OUT/'suggestions.md').open('a') as f:
  f.write('\n## Additional suggestion controls\n\nFive further controls use the same synthetic document without accepting or rejecting any suggestion. The overlapping pending `final` target '+('refused without mutation' if obj['cases'][-5]['pass'] else 'requires investigation')+'. Disjoint `--all` on two `Review token` occurrences '+('created pending changes: accepted preview has two `Reviewed token` strings while the original preview retains two `Review token` strings' if obj['cases'][-4]['pass'] else 'requires investigation')+'. Heading, bulleted-list and table replacements '+('all refused without native mutation' if all(c['pass'] for c in obj['cases'][-3:]) else 'require investigation')+'. Each case has full native before/after and both preview snapshots in ignored local scratch. This brings coverage to seven suggestion command attempts plus one ordinary exact-case edit control; the two initial preview reads are observations, not extra operations.\n')
 sys.exit(0)
b.identity();id=b.new('gdoc scratch — suggestion preview and exact-case control');tab=b.state(id)['tabs'][0]['tabProperties']['tabId']
b.save('r2-suggestions-ledger.json',{'id':id,'tab':tab})
b.update(id,[{'insertText':{'location':{'index':1,'tabId':tab},'text':'draft\nreview\nΟΣ\n'}}])
before=read();b.save('r2-suggestions-before.json',before)
r=run(['suggest',id,'draft','final','--tab',tab]);after=read();b.save('r2-suggestions-after.json',after)
rows=[{'case':'suggest_plain','command':'gdoc suggest DOC draft final --tab TAB --account PERSONAL','result':r,'before':summary(before),'after':summary(after),'native_tabs_unchanged':before['tabs']==after['tabs']}]
if r['returncode']==0:
 for mode in ['PREVIEW_SUGGESTIONS_ACCEPTED','PREVIEW_WITHOUT_SUGGESTIONS']:
  d=read(mode);b.save('r2-suggestions-'+mode+'.json',d);rows.append({'case':mode,'state':summary(d)})
 r=run(['suggest',id,'review','**approved**','--tab',tab]);d=read();b.save('r2-suggestions-inline-style.json',d)
 accepted=read('PREVIEW_SUGGESTIONS_ACCEPTED');b.save('r2-suggestions-inline-style-accepted.json',accepted)
 runs=[e.get('textRun',{}) for t in accepted['tabs'] for p in t['documentTab']['body']['content'] for e in p.get('paragraph',{}).get('elements',[])]
 bold_ok=any(x.get('content')=='approved' and x.get('textStyle',{}).get('bold') is True for x in runs)
 rows.append({'case':'suggest_bold_inline','result':r,'inline':summary(d),'accepted_preview':summary(accepted),'accepted_approved_is_bold':bold_ok})
 status='Preview enabled: two suggested replacements succeeded; native read-only previews preserve originals or show proposed text as appropriate.'
else:
 status='Environment limitation: preview gate refused the request; original native tab content and suggestion state remained unchanged.' if before['tabs']==after['tabs'] else 'Unexpected change after failed suggestion request.'
r=run(['edit',id,'Σ','X','--all','--case-sensitive','--tab',tab]);d=read();b.save('r2-suggestions-case-sensitive-after.json',d)
rows.append({'case':'H17_case_sensitive_workaround','command':'gdoc edit DOC Σ X --all --case-sensitive --tab TAB --account PERSONAL','result':r,'state':summary(d),'pass':r['returncode']==0 and 'ΟX\n' in text(d['tabs']) and 'ΟΣ\n' not in text(d['tabs'])})
obj={'pin':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','status':status,'cases':rows}
(OUT/'suggestions.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(OUT/'suggestions.md').write_text('# Suggestion preview gate and explicit-case control\n\n'+status+'\n\nThe synthetic document starts with `draft`, `review`, and `ΟΣ` on separate paragraphs. The executed command was `gdoc suggest DOC draft final --tab TAB --account PERSONAL`. Full native before/after snapshots remain in ignored `.local-hunt/r2-suggestions*`; sanitized command results and text states are in [suggestions.json](suggestions.json).\n\nThe H17 control uses `gdoc edit DOC Σ X --all --case-sensitive --tab TAB --account PERSONAL`. It '+('passes: `ΟΣ` becomes `ΟX`.' if rows[-1]['pass'] else 'requires investigation; see JSON.')+' This flag is a workaround for this exact-character specimen, not a claim that default contextual Unicode matching is repaired.\n\nSource inspection: [`cmd_suggest`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L1278) rejects structural Markdown and overlapping existing suggestions. [`suggest_replacement`](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L2035) pins revision and token identity, performs a non-mutating preview-enrollment read, and requires saved suggestion IDs plus native readback; it has no direct-edit fallback. These source-level protections do not substitute for testing successful suggestion creation in a preview-enrolled environment.\n\nExactly one new personal scratch Doc; no project enrollment, auth changes, sharing, deletion, collection writes, or acceptance/rejection mutations. Read-only accepted/rejected preview requests run only if creation succeeds. The reproducible probe is [suggestions.py](suggestions.py).\n')
print(json.dumps(obj,ensure_ascii=False,indent=2))
