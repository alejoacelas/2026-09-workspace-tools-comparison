"""Update the guide and verify/export the growing collection."""
import json,sys
import live as b
commit=sys.argv[1]
c=json.loads((b.LOCAL/'collection.json').read_text());id=c['id'];d=b.state(id)
n=len(c['cases'])
guide='\n'.join([
 'gdoc bug hunt — confirmed cases',
 f'{n} live-confirmed examples from parallel investigations',
 'The first round tested 68 offline specimens. Continued rounds exercise document reads and edits, smart chips, merged cells, Unicode matching, spreadsheet imports, comments, navigation and image commands against synthetic personal-account fixtures. Counts describe deliberately difficult examples, not a real-world error rate.',
 'How to read the cases',
 'Each tab contains a reconstructed Pillow Before / Expected / Observed illustration, then Bug, Commands, setup and evidence. Pictures are not screenshots; person names are anonymized. Some failures change stored content; others affect only what a reader or machine-readable output reports. Related triggers can share one repair area.',
 'Scope',
 'Target: public gdoc v0.21.0, commit dbfa4c34. Native write --tab uses a different converter from whole-document Drive import. Passing default-cat controls establish preservation of the specific tested content, not complete document fidelity. These are investigation fixtures, not patches or tests already integrated into upstream gdoc CI.',
 'Ground truth',
 'Explicit input expectations, native Google state, rendered PDF checks and selected Workspace calls establish the outcomes. Google and gdoc can differ in Unicode normalization policy, so disagreement alone is not automatically a bug. The Greek example is stronger: gdoc refuses a literal character that is visibly present. Workspace shares the reference Markdown parser; its agreement is not an independent parser vote.',
 'Controls and exclusions',
 'Passing controls and rejected hypotheses remain in the evidence. Ordinary edits beside chips, explicit merged-cell coordinates, navigation and image inventory worked in the tested cases. Unsupported TSV quoting, documented formatted-value conversions and already-known variants are distinguished from additional confirmed defects.',
 'Evidence and runnable reproducers',''])
tab=c['guide_tab'];d=b.state(id);body=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)['documentTab']['body']['content'];end=body[-1]['endIndex']-1
u=lambda s:len(s.encode('utf-16-le'))//2
req=[]
if end>1:req.append({'deleteContentRange':{'range':{'tabId':tab,'startIndex':1,'endIndex':end}}})
req.append({'insertText':{'location':{'tabId':tab,'index':1},'text':guide}})
rg={'tabId':tab,'startIndex':1,'endIndex':1+u(guide)}
req.extend([{'updateTextStyle':{'range':rg,'textStyle':{'weightedFontFamily':{'fontFamily':'Arial'},'fontSize':{'magnitude':11,'unit':'PT'}},'fields':'weightedFontFamily,fontSize'}},{'updateParagraphStyle':{'range':rg,'paragraphStyle':{'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'}},'fields':'spaceAbove,spaceBelow'}}])
for title,style in [('gdoc bug hunt — confirmed cases','TITLE'),('How to read the cases','HEADING_2'),('Scope','HEADING_2'),('Ground truth','HEADING_2'),('Controls and exclusions','HEADING_2')]:
 start=1+u(guide[:guide.index(title)]);req.append({'updateParagraphStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+u(title)},'paragraphStyle':{'namedStyleType':style,'keepWithNext':True},'fields':'namedStyleType,keepWithNext'}})
label='Evidence and runnable reproducers';start=1+u(guide[:guide.index(label)])
req.append({'updateTextStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+u(label)},'textStyle':{'link':{'url':'https://github.com/alejoacelas/2026-09-workspace-tools-comparison/tree/main/hunt'}},'fields':'link'}})
b.update(id,req)
# Apply page geometry to every document tab; tab-specific defaults can differ.
layout=[]
for t in b.state(id)['tabs']:
 layout.append({'updateDocumentStyle':{'tabId':t['tabProperties']['tabId'],'documentStyle':{'marginTop':{'magnitude':36,'unit':'PT'},'marginBottom':{'magnitude':36,'unit':'PT'},'marginLeft':{'magnitude':54,'unit':'PT'},'marginRight':{'magnitude':54,'unit':'PT'}},'fields':'marginTop,marginBottom,marginLeft,marginRight'}})
b.update(id,layout)
# Synchronize reviewed explanations and fix notes without rewriting figures or commands.
manifest=json.loads((b.ROOT/'hunt/confirmed.json').read_text())
notes=[]
for case in manifest:
 tab=c['cases'][case['id']]
 native=next(t for t in b.state(id)['tabs'] if t['tabProperties']['tabId']==tab)['documentTab']
 for element in native['body']['content']:
  line=''.join(e.get('textRun',{}).get('content','') for e in element.get('paragraph',{}).get('elements',[]))
  desired=None
  if line.startswith('Bug. '):desired='Bug. '+case['bug']+'\n'
  if line.startswith('Evidence: '):desired='Evidence: '+case.get('evidence_label','Live native readback; command returned success.')+' '+case['novelty']+'\n'
  if desired is not None and line!=desired:
   notes.append({'replaceAllText':{'containsText':{'text':line,'matchCase':True},'replaceText':desired,'tabsCriteria':{'tabIds':[tab]}}})
if notes:b.update(id,notes)
d=b.state(id);links=[]
for case in manifest:
 if not case.get('fix_url'):continue
 tab=c['cases'][case['id']]
 native=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)['documentTab']
 for p in native['body']['content']:
  for e in p.get('paragraph',{}).get('elements',[]):
   text=e.get('textRun',{}).get('content','')
   if 'PR #66' in text:
    start=e['startIndex']+u(text[:text.index('PR #66')]);links.append({'updateTextStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+6},'textStyle':{'link':{'url':case['fix_url']}},'fields':'link'}})
if links:b.update(id,links)
d=b.state(id);b.save('collection-native.json',d)
assert len(d['tabs'])==n+1
checks=[]
for key,tab in c['cases'].items():
 t=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)['documentTab'];assert len(t['inlineObjects'])==1
 from confirm import text
 words=text(t['body']);assert words.index('Bug.')<words.index('Commands')<words.index('Evidence:')
 checks.append({'case':key,'images':len(t['inlineObjects']),'description_command_order':True})
(b.ROOT/'hunt/publication-checks.json').write_text(json.dumps({'tabs':len(d['tabs']),'cases':checks,'pdf_visual_qa':'pending'},indent=2)+'\n')
r=b.cli(['export',id,'--out',str(b.LOCAL/'collection.pdf')]);assert r['returncode']==0,r
print(f'Verified {n+1} tabs / {n} images; exported collection.pdf',flush=True)
