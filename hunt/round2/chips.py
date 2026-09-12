"""Live synthetic smart-chip reads. Only creates its own private scratch document."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import live as b
rows=[('control','Control: Example Owner owns budget.','text'),('person_sentence','Person: @ owns budget.','person'),('person_alone','Solo: @','person'),('person_bold_neighbor','Bold: Before @ after.','person'),('person_link_neighbor','Link: Policy @ after.','person'),('date','Date: @ due.','date'),('file','File: @ attached.','richLink')]
doc=b.new('Synthetic smart-chip read specimen');b.save('r2-chips-ledger.json',{'document_id':doc})
source='\n'.join(r[1] for r in rows)+'\n';b.update(doc,[{'insertText':{'location':{'index':1},'text':source}}])
d=b.state(doc);tab=d['tabs'][0]['tabProperties']['tabId'];setup=[]
# Work backwards so replacement ranges for earlier markers stay stable even if a
# native element uses multiple UTF-16 units. Each optional type gets its own batch.
for name,line,kind in reversed(rows):
 if kind=='text':continue
 index=source.index(line)+line.index('@')+1
 props={'person':{'email':b.ACCOUNT},'date':{'timestamp':'2030-01-02T12:00:00Z','dateFormat':'DATE_FORMAT_ISO8601'},'richLink':{'uri':'https://docs.google.com/document/d/'+doc+'/edit'}}[kind]
 request={'person':('insertPerson','personProperties'),'date':('insertDate','dateElementProperties'),'richLink':('insertRichLink','richLinkProperties')}[kind]
 try:
  b.update(doc,[{'deleteContentRange':{'range':{'startIndex':index,'endIndex':index+1,'tabId':tab}}},{request[0]:{'location':{'index':index,'tabId':tab},request[1]:props}}])
  setup.append({'case':name,'created':True})
 except Exception as e:setup.append({'case':name,'created':False,'error_type':type(e).__name__})
d=b.state(doc)
styles=[]
for el in d['tabs'][0]['documentTab']['body']['content']:
 for elem in el.get('paragraph',{}).get('elements',[]):
  content=elem.get('textRun',{}).get('content','')
  for word,style in [('Before',{'bold':True}),('Policy',{'link':{'url':'https://example.com/policy'}})]:
   if word in content:
    start=elem['startIndex']+content.index(word)
    styles.append({'updateTextStyle':{'range':{'startIndex':start,'endIndex':start+len(word),'tabId':tab},'textStyle':style,'fields':','.join(style)}})
if styles:b.update(doc,styles)
d=b.state(doc);b.save('r2-chips-native.json',d)
paragraphs=[e['paragraph'] for e in d['tabs'][0]['documentTab']['body']['content'] if 'paragraph' in e]
private_values={b.ACCOUNT:'PERSON_EMAIL',doc:'DOC',tab:'TAB'}
for p in paragraphs:
 for e in p.get('elements',[]):
  props=e.get('person',{}).get('personProperties',{})
  for k,v in props.items():
   if k in ('name','email') and v:private_values[v]='PERSON' if k=='name' else 'PERSON_EMAIL'
def clean(v):
 if isinstance(v,str):
  for raw,replacement in sorted(private_values.items(),key=lambda x:-len(x[0])):v=v.replace(raw,replacement)
  return v
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k not in ('personId','richLinkId','dateId','headingId')}
 return v
observations=[]
for name,line,kind in rows:
 prefix=line.split(':')[0]+':'
 para=next((p for p in paragraphs if any(e.get('textRun',{}).get('content','').startswith(prefix) for e in p.get('elements',[]))),{})
 elements=para.get('elements',[])
 native_types=[k for e in elements for k in ('textRun','person','dateElement','richLink') if k in e]
 observations.append({'case':name,'prefix':prefix,'native_types':native_types,'native_elements':clean(elements),'kind':kind})
reads=[]
for route,args in [('default',['cat',doc]),('selected_tab',['cat',doc,'--tab',tab])]:
 r=b.cli(args);b.save('r2-chips-'+route+'-cli.json',r)
 reads.append({'route':route,'returncode':r['returncode'],'stdout':clean(r['stdout']),'stderr':clean('\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:')))})
result={'revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','scope':'seven synthetic paragraphs, two read routes; self-person identity anonymized','setup':setup,'native':observations,'reads':reads}
(b.ROOT/'hunt/round2/chips-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'setup':setup,'native_types':[(x['case'],x['native_types']) for x in observations],'reads':reads},indent=2,ensure_ascii=False))
