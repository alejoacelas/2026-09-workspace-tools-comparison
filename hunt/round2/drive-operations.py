"""Bounded personal Drive filename/identity checks, all queries folder-scoped."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
from gdoc.api.drive import _escape_query_value
LOCAL='r2-drive-ledger.json';ledger={};rows=[]
def remember(key,id):ledger[key]=id;b.save(LOCAL,ledger);return id
def clean(s):
 for key,id in sorted(ledger.items(),key=lambda x:-len(x[1])):s=s.replace(id,key.upper())
 return s.replace(b.ACCOUNT,'PERSONAL').replace(str(b.ROOT),'PROJECT')
def call(args):
 r=b.cli(args+['--json']);obj=None
 if r['returncode']==0:
  try:obj=json.loads(r['stdout'])
  except json.JSONDecodeError:pass
 return r,obj
def info(id):return b.drive.files().get(fileId=id,fields='id,name,parents,mimeType',supportsAllDrives=True).execute()
def record(case,r,ok,**detail):
 row={'case':case,'returncode':r['returncode'],'passed':bool(ok),'stderr':clean('\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:'))),**detail};rows.append(row)
 (b.ROOT/'hunt/round2/drive-operations.json').write_text(json.dumps({'revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','scope':'one dedicated synthetic folder with child folder; exact native title/parent/identity/content checks; every search/list explicitly scoped','cases':rows},indent=2,ensure_ascii=False)+'\n');print(case,ok,flush=True)
def ids_from(obj):
 if isinstance(obj,list):return {x['id'] for x in obj}
 if isinstance(obj,dict):
  for key in ['files','results','items']:
   if key in obj:return {x['id'] for x in obj[key]}
 raise ValueError('Unexpected CLI file-list JSON shape')
def scoped_native(folder):
 response=b.drive.files().list(q="'%s' in parents and trashed=false"%folder,fields='files(id,name)',pageSize=1000).execute()
 return response['files']
r,o=call(['mkdir','Synthetic Drive operations audit']);root=remember('root',o['id']);record('mkdir_standard',r,info(root)['name']=='Synthetic Drive operations audit')
r,o=call(['mkdir',"Owner's archive (Σ)",'--parent',root]);child=remember('child',o['id']);actual=info(child);record('mkdir_punctuation_unicode',r,actual['name']=="Owner's archive (Σ)" and actual['parents']==[root],name=actual['name'])
r,o=call(['new','Budget draft','--folder',root,'--paged']);source=remember('source',o['id']);record('new_standard',r,info(source)['name']=='Budget draft' and info(source)['parents']==[root])
b.update(source,[{'insertText':{'location':{'index':1},'text':'SYNTHETIC EXACT BODY\n'}}])
for label,name in [('apostrophe',"Director's notes"),('backslash',r'Archive\2026'),('parentheses','Plan (Q4)'),('unicode','Café Σ budget')]:
 r,o=call(['rename',source,name]);actual=info(source);record('rename_'+label,r,r['returncode']==0 and actual['name']==name and actual['id']==source and actual['parents']==[root],name=actual['name'])
 # Use gdoc's own literal escape helper but explicitly scope the raw query. The
 # normal find/--title route exposes no folder restriction and is not run here.
 query="'%s' in parents and trashed=false and name = '%s'"%(root,_escape_query_value(name))
 r,o=call(['find',query,'--raw']);got=ids_from(o) if o is not None else set()
 record('scoped_exact_find_'+label,r,r['returncode']==0 and got=={source},query=clean(query),result_names=[x['name'] for x in (o.get('files',[]) if isinstance(o,dict) else (o or []))])
copyname="Director's copy \\ (Σ)";r,o=call(['cp',source,copyname]);copy=remember('copy',o['id']);copied=info(copy);original=info(source)
def doc_text(id):
 d=b.state(id);return ''.join(e.get('textRun',{}).get('content','') for p in d['tabs'][0]['documentTab']['body']['content'] for e in p.get('paragraph',{}).get('elements',[]))
record('copy_identity_name_content',r,r['returncode']==0 and copy!=source and copied['name']==copyname and original['name']=='Café Σ budget' and doc_text(copy)==doc_text(source),copy_name=copied['name'],different_identity=copy!=source,source_name_unchanged=original['name']=='Café Σ budget',copy_in_source_folder=copied.get('parents')==[root])
r,o=call(['mv',copy,child]);record('move_copy_only',r,r['returncode']==0 and info(copy)['parents']==[child] and info(source)['parents']==[root])
r,o=call(['mv',copy,child]);record('repeat_move_keeps_destination',r,r['returncode']==0 and info(copy)['parents']==[child])
# One compound check covers both containing folders without an account-wide scan.
details=[];ok=True;last=None
for label,folder in [('root',root),('child',child)]:
 native=scoped_native(folder);r,o=call(['ls',folder]);got=ids_from(o) if o is not None else set();passed=r['returncode']==0 and got=={x['id'] for x in native};ok &= passed;last=r;details.append({'folder':label,'passed':passed,'native_names':sorted(x['name'] for x in native),'result_count':len(got)})
record('scoped_list_both_folders',last,ok,folders=details)
