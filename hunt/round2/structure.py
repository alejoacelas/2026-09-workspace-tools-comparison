"""15 personal synthetic live structure probes; no sharing/deletion/collection writes.
Run with repos/gdoc/.venv/bin/python hunt/round2/structure.py.
"""
import io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'hunt'))
import live as b
from googleapiclient.http import MediaIoBaseUpload
OUT=ROOT/'hunt/round2'; OUT.mkdir(exist_ok=True)
ledger=json.loads((b.LOCAL/'r2-structure-ledger.json').read_text()) if (b.LOCAL/'r2-structure-ledger.json').exists() else []
results=json.loads((OUT/'structure-results.json').read_text())['cases'] if (OUT/'structure-results.json').exists() else []

def redact_notes(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k=='stderr' and isinstance(v,str):x[k]='\n'.join(line for line in v.splitlines() if line.startswith(('ERR:','WARN:')))
   else:redact_notes(v)
 elif isinstance(x,list):
  for v in x:redact_notes(v)
redact_notes(results)

def txt(x):
 if isinstance(x,dict):
  if 'textRun' in x:return x['textRun'].get('content','')
  return ''.join(txt(v) for v in x.values())
 if isinstance(x,list):return ''.join(txt(v) for v in x)
 return ''

def summarise(doc):
 tab=doc['tabs'][0];dt=tab['documentTab'];content=dt['body']['content'];tables=[]
 for el in content:
  if 'table' in el:
   t=el['table'];tables.append({'rows':t['rows'],'columns':t['columns'],'cells':[[{'text':txt(c).rstrip('\n'),'rowSpan':c.get('tableCellStyle',{}).get('rowSpan',1),'columnSpan':c.get('tableCellStyle',{}).get('columnSpan',1)} for c in row['tableCells']] for row in t['tableRows']]})
 ids={k:'list-'+str(i) for i,k in enumerate(dt.get('lists',{}))}
 paras=[]
 for e in content:
  if 'paragraph' not in e:continue
  p=e['paragraph'];q={'text':txt(p).rstrip('\n'),'start':e.get('startIndex'),'end':e.get('endIndex')}
  if 'bullet' in p:q['bullet']={**p['bullet'],'listId':ids.get(p['bullet']['listId'],'list-unknown')}
  paras.append(q)
 return {'text':txt(dt['body']),'tables':tables,'paragraphs':paras,'lists':[{ 'label':ids[k],'levels':v.get('listProperties',{}).get('nestingLevels',[])} for k,v in dt.get('lists',{}).items()]}

def scrub(r,id,tab):
 r={**r,'stderr':'\n'.join(line for line in r.get('stderr','').splitlines() if line.startswith(('ERR:','WARN:')))}
 return {k:v.replace(id,'DOC').replace(tab,'TAB').replace(b.ACCOUNT,'PERSONAL').replace(str(ROOT),'PROJECT') if isinstance(v,str) else v for k,v in r.items()}

def create(name,html):
 existing=next((r['id'] for r in ledger if r['case']==name),None)
 if existing:return existing
 b.identity()
 id=b.drive.files().create(body={'name':'Synthetic r2 structure '+name,'mimeType':'application/vnd.google-apps.document'},media_body=MediaIoBaseUpload(io.BytesIO(('<html><body>'+html+'</body></html>').encode()),mimetype='text/html',resumable=False),fields='id').execute()['id']
 ledger.append({'case':name,'id':id});b.save('r2-structure-ledger.json',ledger)
 return id

def record(row):
 results[:]=[r for r in results if r['id']!=row['id']]
 results.append(row)
 (OUT/'structure-results.json').write_text(json.dumps({'pin':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','account':'personal verified','cases':results},indent=2)+'\n')
 print(row['id'],row['assessment'],flush=True)

TABLES=[
 ('regular_coordinate','<table><tr><td>A</td><td>B</td><td>C</td></tr><tr><td>D</td><td>E</td><td>F</td></tr></table>','1,2','F'),
 ('colspan_rightmost','<table><tr><td colspan="2">Merged A</td><td>C</td></tr><tr><td>D</td><td>E</td><td>F</td></tr></table>','0,2','C'),
 ('colspan_wrong_column','<table><tr><td colspan="2">Merged A</td><td>C</td><td>D</td></tr><tr><td>E</td><td>F</td><td>G</td><td>H</td></tr></table>','0,2','C'),
 ('rowspan_wrong_column','<table><tr><td rowspan="2">Merged A</td><td>B</td><td>C</td></tr><tr><td>D</td><td>E</td></tr></table>','1,1','D'),
 ('colspan_unmerged_row_control','<table><tr><td colspan="2">Merged A</td><td>C</td></tr><tr><td>D</td><td>E</td><td>F</td></tr></table>','1,2','F'),
 ('colspan_label_control','<table><tr><td colspan="2">Merged A</td><td>C</td></tr></table>','Merged A','C'),
 ('multiline_cell_edit','<table><tr><td>Label</td><td><p>North</p><p>South</p></td></tr><tr><td>Keep</td><td>900</td></tr></table>','0,1','North\nSouth'),
 ('empty_cell_edit','<table><tr><td>Label</td><td></td></tr><tr><td>Keep</td><td>900</td></tr></table>','0,1',''),
 ('multiline_label_control','<table><tr><td><p>North</p><p>South</p></td><td>100</td></tr></table>','North\nSouth','100'),
]

for name,html,cell,target in TABLES:
 if any(r['id']==name for r in results):continue
 id=create(name,html);doc=b.state(id);tab=doc['tabs'][0]['tabProperties']['tabId'];before=summarise(doc)
 b.save('r2-structure-'+name+'-before.json',doc)
 read=b.cli(['cat',id,'--tab',tab]);command=['edit',id,'Updated','--cell',cell,'--tab',tab]
 edit=b.cli(command);afterdoc=b.state(id);b.save('r2-structure-'+name+'-after.json',afterdoc);after=summarise(afterdoc)
 oldcells=[c['text'] for t in before['tables'] for row in t['cells'] for c in row];newcells=[c['text'] for t in after['tables'] for row in t['cells'] for c in row]
 target_index=oldcells.index(target) if target in oldcells else None
 expected=oldcells.copy()
 if target_index is not None:expected[target_index]='Updated'
 span_needed='colspan' in name or 'rowspan' in name
 span_verified=any(c['rowSpan']>1 or c['columnSpan']>1 for t in before['tables'] for row in t['cells'] for c in row)
 eligible=target_index is not None and (not span_needed or span_verified)
 ok=eligible and edit['returncode']==0 and newcells==expected
 record({'id':name,'html':html,'command':['edit','DOC','Updated','--cell',cell,'--tab','TAB','--account','PERSONAL'],'native_span_verified':span_verified,'intended_cell_text':target,'before':before,'read':scrub(read,id,tab),'edit':scrub(edit,id,tab),'after':after,'expected_cell_texts':expected,'assessment':'pass' if ok else 'candidate' if eligible else 'fixture-unestablished'})

# Content-preservation control for multiline cells, without forcing TSV roundtrip grammar.
name='multiline_read_control';id=create(name,'<table><tr><td><p>North</p><p>South</p></td><td><p>100</p><p>200</p></td></tr></table>');doc=b.state(id);tab=doc['tabs'][0]['tabProperties']['tabId'];reads={route:scrub(b.cli(['cat',id]+(['--tab',tab] if route=='selected' else [])),id,tab) for route in ['default','selected']}
record({'id':name,'before':summarise(doc),'reads':reads,'assessment':'pass' if all(all(s in r['stdout'] for s in ['North','South','100','200']) for r in reads.values()) else 'candidate'})

LISTS=[('decimal_control','NUMBERED_DECIMAL_ALPHA_ROMAN',False),('upper_alpha_known_variant','NUMBERED_UPPERALPHA_ALPHA_ROMAN',False),('upper_roman_known_variant','NUMBERED_UPPERROMAN_UPPERALPHA_DECIMAL',False),('resumed_same_list_known_variant','NUMBERED_DECIMAL_ALPHA_ROMAN',True),('separate_lists_known_variant','NUMBERED_DECIMAL_ALPHA_ROMAN',False)]
for name,preset,resume in LISTS:
 if any(r['id']==name for r in results):continue
 id=create(name,'<p>Review</p><p>Note</p><p>Approve</p>');doc=b.state(id);tab=doc['tabs'][0]['tabProperties']['tabId'];p=[e for e in doc['tabs'][0]['documentTab']['body']['content'] if 'paragraph' in e]
 start=p[0]['startIndex'];end=p[-1]['endIndex']-1
 b.update(id,[{'createParagraphBullets':{'range':{'startIndex':start,'endIndex':end,'tabId':tab},'bulletPreset':preset}}])
 if resume:b.update(id,[{'deleteParagraphBullets':{'range':{'startIndex':p[1]['startIndex'],'endIndex':p[1]['endIndex']-1,'tabId':tab}}}])
 if name=='separate_lists_known_variant':
  b.update(id,[{'deleteParagraphBullets':{'range':{'startIndex':start,'endIndex':end,'tabId':tab}}}])
  b.update(id,[{'createParagraphBullets':{'range':{'startIndex':start,'endIndex':p[0]['endIndex']-1,'tabId':tab},'bulletPreset':preset}},{'createParagraphBullets':{'range':{'startIndex':p[2]['startIndex'],'endIndex':end,'tabId':tab},'bulletPreset':'NUMBERED_UPPERALPHA_ALPHA_ROMAN'}}])
 doc=b.state(id);b.save('r2-structure-'+name+'-native.json',doc);reads={route:scrub(b.cli(['cat',id]+(['--tab',tab] if route=='selected' else [])),id,tab) for route in ['default','selected']}
 record({'id':name,'before':summarise(doc),'reads':reads,'assessment':'control-or-known-list-family','note':'Native glyph/list identity must be inspected; not counted as new H09-independent family.'})

# Independent fresh-fixture replay plus an explicit logical-column control.
merged_case=next(r for r in results if r['id']=='colspan_label_control')
merged_case['assessment']='live-confirmed-wrong-target'
if 'replication' not in merged_case:
 name='merged_label_replication';id=create(name,'<table><tr><td colspan="3">Budget</td><td>700</td></tr></table>');doc=b.state(id);tab=doc['tabs'][0]['tabProperties']['tabId'];before=summarise(doc)
 b.save('r2-structure-'+name+'-before.json',doc)
 r=b.cli(['edit',id,'800','--cell','Budget','--tab',tab]);afterdoc=b.state(id);b.save('r2-structure-'+name+'-after.json',afterdoc)
 merged_case['replication']={'before':before,'command':['edit','DOC','800','--cell','Budget','--tab','TAB'],'result':scrub(r,id,tab),'after':summarise(afterdoc)}
 name='merged_label_explicit_column_control';id=create(name,'<table><tr><td colspan="2">Merged A</td><td>C</td></tr></table>');doc=b.state(id);tab=doc['tabs'][0]['tabProperties']['tabId'];before=summarise(doc)
 b.save('r2-structure-'+name+'-before.json',doc)
 r=b.cli(['edit',id,'Updated','--cell','Merged A','--col','2','--tab',tab]);afterdoc=b.state(id);b.save('r2-structure-'+name+'-after.json',afterdoc)
 merged_case['explicit_column_control']={'before':before,'command':['edit','DOC','Updated','--cell','Merged A','--col','2','--tab','TAB'],'result':scrub(r,id,tab),'after':summarise(afterdoc)}
 record(merged_case)

lines=['# Round 2: live native structure probes','',f'{len(results)} cases on fresh personal synthetic documents. Pinned gdoc CLI, verified personal identity before writes; no collection edits, sharing, or deletions.','', '| Case | Assessment |','|---|---|']
for r in results:lines.append('| '+r['id']+' | '+r['assessment']+' |')
lines+=['','## Confirmed: merged label routes into a covered cell','', 'The CLI promises a label replaces “the cell to its right”; `--col` selects an explicit zero-based column. In a one-row native table with Merged A spanning two columns followed by C, `gdoc edit DOC Updated --cell \"Merged A\" --tab TAB` returns success but changes the left cell to Merged AUpdated and leaves C untouched. A fresh three-column-span replay changes Budget to Budget800 while leaving the intended adjacent value 700 unchanged. An explicit `--col 2` on a pristine two-span control correctly changes C to Updated and preserves Merged A.','', 'Root boundary: resolve_cell_range uses ci + 1 for the default target without accounting for columnSpan. The native array includes a covered empty cell at that physical slot. The resolver selects its editable position; Google incorporates the inserted text into the owning merged cell. It does not skip to the next visible cell. This is a new merged-topology trigger in the broader target-identity repair area, not a claim that merged coordinate addressing generally fails. All four suspect coordinate examples passed.','', 'Evidence is the case colspan_label_control, including separate replication and explicit_column_control captures. Both erroneous edits and the workaround returned exit 0, with native Docs readback. [CLI label promise](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/cli.py#L3996), [cell resolver](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L652).','', '## Controls and known-family observations','', 'Nine table/content scenarios passed their selected checks: normal/merged/rowspan coordinate targets, unmerged row below a span, multiline replacement, empty-cell insertion, multiline label selection, and retention of multiline cell values. These controls do not certify arbitrary merged topology or document style preservation.','', 'Five live list scenarios add real native evidence rather than new families. Decimal 1–3 agrees across default and selected-tab reads. UPPER_ALPHA and UPPER_ROMAN glyph metadata is real, but both exports render decimal markers: a representation limitation affecting both routes. A resumed native DECIMAL list keeps one listId around intervening prose; default cat returns 1 then 2, while selected-tab cat returns 1 then 1. That is the already-known ordinal-state family. Distinct-list controls restart, as intended.','', 'Fifteen main cases were run, plus a fresh merged-label replication and an explicit-column control. Initial list setup used an obsolete preset name, which Google rejected before mutation; the harness corrected it from the discovery enum and reused the same scratch document. That setup error is excluded from app findings.','', 'All HTML-imported table spans were checked in the native Docs response before judging cell coordinates. Expected coordinates refer to the displayed logical row/column; these native physical cell arrays retain covered positions that are not separate visible cells. Full input HTML, native span/cell summaries, commands and results are in [structure-results.json](structure-results.json). IDs and full resource snapshots remain in ignored local scratch.','', 'List probes deliberately revisit known ordinal/marker-state mechanisms as controls; they are not automatically new bug families. Multiline read checks require retained values, not a specific TSV representation.']
(OUT/'structure-results.md').write_text('\n'.join(lines)+'\n')
