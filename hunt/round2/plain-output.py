"""Live TSV escaping scope checks on already-owned synthetic Drive fixtures."""
import csv,io,json,sys
from pathlib import Path
from googleapiclient.errors import HttpError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
ledger=json.loads((b.LOCAL/'r2-drive-ledger.json').read_text());doc=ledger['source'];folder=ledger['root'];tab=b.state(doc)['tabs'][0]['tabProperties']['tabId'];ledger['tab']=tab;b.save('r2-plain-ledger.json',ledger)
meta=b.drive.files().get(fileId=doc,fields='owners(displayName,emailAddress)').execute()
private={v:k.upper() for k,v in ledger.items()};private[b.ACCOUNT]='PERSON_EMAIL'
for owner in meta.get('owners',[]):
 for k,v in owner.items():
  if v:private[v]='PERSON_EMAIL' if k=='emailAddress' else 'PERSON'
def clean(x):
 if isinstance(x,str):
  for raw,value in sorted(private.items(),key=lambda x:-len(x[0])):x=x.replace(raw,value)
  return x.replace(str(b.ROOT),'PROJECT')
 if isinstance(x,list):return [clean(v) for v in x]
 return x
rows=[]
def publish():
 (b.ROOT/'hunt/round2/plain-output.json').write_text(json.dumps({'revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','family':'H18 machine-readable delimiter escaping; not new independent bugs','reader':'Python csv.reader delimiter TAB, quotechar double quote, strict=True','cases':rows},indent=2,ensure_ascii=False)+'\n')
def execute(name,command,title):
 plain=b.cli(command+['--plain']);structured=b.cli(command+['--json']);b.save('r2-plain-'+name+'-raw.json',{'plain':plain,'json':structured})
 parsed=list(csv.reader(io.StringIO(plain['stdout']),delimiter='\t',quotechar='"',strict=True));obj=json.loads(structured['stdout'])
 if command[0]=='ls':
  target=next(x for x in obj['files'] if x['id']==doc);json_ok=target['name']==title
  match=[r for r in parsed if r and r[0]==doc];plain_ok=len(match)==1 and len(match[0])==3 and match[0][1]==title and len(parsed)==len(obj['files'])
 elif command[0]=='info':
  json_ok=obj['title']==title;match=[r for r in parsed if r and r[0]=='title'];plain_ok=len(match)==1 and len(match[0])==2 and match[0][1]==title and all(len(r)==2 for r in parsed)
 else:
  target=next(x for x in obj['tabs'] if x['id']==tab);json_ok=target['title']==title;match=[r for r in parsed if r and r[0]==tab];plain_ok=len(match)==1 and len(match[0])==2 and match[0][1]==title and len(parsed)==len(obj['tabs'])
 rows.append({'case':name,'command':command[0],'native_title':title,'plain_returncode':plain['returncode'],'json_returncode':structured['returncode'],'plain_roundtrips_title_and_record_shape':plain_ok,'json_roundtrips_title':json_ok,'plain_stdout':clean(plain['stdout']),'csv_reader_records':clean(parsed)})
 publish();print(name,'plain',plain_ok,'json',json_ok,flush=True)
# Ordinary records first establish that the parser/expected field counts agree.
assert b.cli(['rename',doc,'Café Σ budget'])['returncode']==0
normal=b.drive.files().get(fileId=doc,fields='name').execute()['name'];execute('ls_ordinary_control',['ls',folder],normal)
normal_tab=b.state(doc)['tabs'][0]['tabProperties']['title'];execute('tabs_ordinary_control',['tabs',doc],normal_tab)
bad='Budget\tQ4\nBoard';r=b.cli(['rename',doc,bad]);assert r['returncode']==0
native=b.drive.files().get(fileId=doc,fields='name').execute()['name'];assert native==bad,repr(native)
execute('ls_tab_newline_title',['ls',folder],native);execute('info_tab_newline_title',['info',doc],native)
try:
 b.update(doc,[{'updateDocumentTabProperties':{'tabProperties':{'tabId':tab,'title':bad},'fields':'title'}}])
except HttpError as exc:
 native_tab=b.state(doc)['tabs'][0]['tabProperties']['title']
 rows.append({'case':'tabs_tab_newline_title','status':f'unconfirmed: native setup returned HTTP{exc.resp.status}','requested_title':bad,'native_title_after':native_tab,'reason':'Backend did not establish the requested tab-title fixture; no gdoc output defect inferred.'})
 publish()
else:
 native_tab=b.state(doc)['tabs'][0]['tabProperties']['title']
 if native_tab==bad:execute('tabs_tab_newline_title',['tabs',doc],native_tab)
 else:
  rows.append({'case':'tabs_tab_newline_title','status':'unconfirmed: native title differs from requested fixture','requested_title':bad,'native_title_after':native_tab})
  publish()
