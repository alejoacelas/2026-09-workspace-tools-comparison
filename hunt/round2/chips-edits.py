"""Live chip/edit interactions on NEW synthetic fixtures, never the read fixture."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
CASES=[
 ('plain_control','Status draft.\n',None,'edit','draft','final'),
 ('person_before_target','Owner: @ status draft.\n','person','edit','draft','final'),
 ('person_after_target','Status draft owned by @.\n','person','edit','draft','final'),
 ('file_before_target','Plan @ status draft.\n','richLink','edit','draft','final'),
 ('person_cross_gap','Before @ after.\n','person','edit','Before  after','Replacement'),
 ('file_cross_gap','Before @ after.\n','richLink','edit','Before  after','Replacement'),
 ('person_visible_name','Owner: @.\n','person','visible_name',None,'Example Owner'),
 ('person_append','Owner: @.\n','person','append',None,None),
]
def elements(d):
 return [e for p in d['tabs'][0]['documentTab']['body']['content'] for e in p.get('paragraph',{}).get('elements',[])]
def summary(d):
 es=elements(d)
 return {'plain_text':''.join(e.get('textRun',{}).get('content','') for e in es),'person_count':sum('person' in e for e in es),'file_chip_count':sum('richLink' in e for e in es),'elements':es}
ledger=[];out=[]
for name,source,kind,operation,old,new in CASES:
 doc=b.new('Synthetic chip editing '+name);ledger.append({'case':name,'document_id':doc});b.save('r2-chips-edit-ledger.json',ledger)
 b.update(doc,[{'insertText':{'location':{'index':1},'text':source}}]);tab=b.state(doc)['tabs'][0]['tabProperties']['tabId']
 if kind:
  at=source.index('@')+1
  request,props=('insertPerson',{'personProperties':{'email':b.ACCOUNT}}) if kind=='person' else ('insertRichLink',{'richLinkProperties':{'uri':'https://docs.google.com/document/d/'+doc+'/edit'}})
  b.update(doc,[{'deleteContentRange':{'range':{'startIndex':at,'endIndex':at+1,'tabId':tab}}},{request:{'location':{'index':at,'tabId':tab},**props}}])
 before=b.state(doc);b.save('r2-chips-edit-'+name+'-before.json',before)
 control=summary(before);private={b.ACCOUNT:'PERSON_EMAIL',doc:'DOC',tab:'TAB'}
 for e in elements(before):
  for k,v in e.get('person',{}).get('personProperties',{}).items():
   if k in ('name','email') and v:private[v]='PERSON' if k=='name' else 'PERSON_EMAIL'
 if kind:assert control['person_count']+control['file_chip_count']==1
 read=b.cli(['cat',doc,'--tab',tab]);assert read['returncode']==0
 if operation=='visible_name':old=next(e['person']['personProperties'].get('name') or e['person']['personProperties']['email'] for e in elements(before) if 'person' in e)
 if operation=='append':
  file=b.LOCAL/'r2-chips-append.md';file.write_text('Additional sentence.\n');argv=['insert',doc,str(file),'--tab',tab,'--position','end']
 else:argv=['edit',doc,old,new,'--tab',tab]
 r=b.cli(argv);after=b.state(doc);b.save('r2-chips-edit-'+name+'-after.json',after);b.save('r2-chips-edit-'+name+'-cli.json',r)
 def clean(x):
  if isinstance(x,str):
   for raw,replacement in sorted(private.items(),key=lambda y:-len(y[0])):x=x.replace(raw,replacement)
   return x.replace(str(b.ROOT),'PROJECT')
  if isinstance(x,list):return [clean(y) for y in x]
  if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ('personId','richLinkId','headingId')}
  return x
 result={'case':name,'operation':operation,'old_text':clean(old),'new_text':new,'before':clean(control),'after':clean(summary(after)),'returncode':r['returncode'],'stdout':clean(r['stdout']),'stderr':clean('\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:'))),'selected_tab_read_before':clean(read['stdout'])}
 out.append(result);(b.ROOT/'hunt/round2/chips-edits-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
 print(name,r['returncode'],'chips',control['person_count']+control['file_chip_count'],'->',result['after']['person_count']+result['after']['file_chip_count'],repr(result['after']['plain_text']),flush=True)
