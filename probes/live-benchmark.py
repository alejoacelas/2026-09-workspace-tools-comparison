"""Live pinned-CLI vs installed Workspace stdio benchmark on synthetic specimens.
Run with workspace-mcp's Python, --account an explicitly authorized personal account.
Creates files in a dedicated Drive folder; never deletes or shares them. Resource IDs
and transport logs stay in ignored .local-benchmark; published results are redacted.
"""
import argparse, asyncio, csv, json, os, statistics, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'repos/gdoc'))
from gdoc.auth import get_credentials
from googleapiclient.discovery import build
from fastmcp import Client
from fastmcp.client.transports import StdioTransport
P=argparse.ArgumentParser();P.add_argument('--account',required=True);P.add_argument('--trials',type=int,default=5)
args=P.parse_args();ACCOUNT=args.account
LOCAL=ROOT/'.local-benchmark';LOCAL.mkdir(exist_ok=True);LOCAL.chmod(0o700)
OUT=ROOT/'evidence/live-benchmark.json'
creds=get_credentials(ACCOUNT)
drive=build('drive','v3',credentials=creds);docs=build('docs','v1',credentials=creds);sheets=build('sheets','v4',credentials=creds)
results={'started_utc':datetime.now(timezone.utc).isoformat(),'trials':args.trials,'scope':'synthetic personal-account files only','timing':'wall clock; CLI subprocess vs already-connected stdio MCP; oracle/setup excluded','samples':[],'checks':[],'resources_created':0}
ledger=[]
def save():
 OUT.write_text(json.dumps(results,indent=2)+'\n')
 (LOCAL/'ledger.json').write_text(json.dumps(ledger,indent=2));(LOCAL/'ledger.json').chmod(0o600)
def identity():
 actual=drive.about().get(fields='user(emailAddress)').execute()['user']['emailAddress']
 assert actual.lower()==ACCOUNT.lower(),'Google identity mismatch'
def scrub(s):
 s=s.replace(ACCOUNT,'ACCOUNT')
 for r in ledger:s=s.replace(r['id'],'RESOURCE_'+str(ledger.index(r)))
 return s.replace(str(Path.home()),'~')
def created(kind,resource):
 ledger.append({'kind':kind,'id':resource});results['resources_created']=len(ledger);save();return resource
def update(doc,requests):
 identity();return docs.documents().batchUpdate(documentId=doc,body={'requests':requests}).execute()
def docstate(doc):return docs.documents().get(documentId=doc,includeTabsContent=True).execute()
def textof(d):
 def walk(x):
  if isinstance(x,dict):
   if 'textRun' in x:yield x['textRun'].get('content','')
   else:
    for v in x.values():yield from walk(v)
  elif isinstance(x,list):
   for v in x:yield from walk(v)
 return ''.join(walk(d['tabs']))
def newdoc(label,text=''):
 identity();doc=created(label,docs.documents().create(body={'title':'Comparison synthetic — '+label}).execute()['documentId'])
 identity();drive.files().update(fileId=doc,addParents=folder,fields='id').execute()
 if text:update(doc,[{'insertText':{'location':{'index':1},'text':text}}])
 return doc
async def cli(argv):
 env={**os.environ,'GDOC_AUTO_UPDATE':'0','PYTHONPATH':str(ROOT/'repos/gdoc')}
 p=await asyncio.create_subprocess_exec(str(ROOT/'repos/gdoc/.venv/bin/python'),'-m','gdoc',*argv,'--account',ACCOUNT,cwd=ROOT/'repos/gdoc',env=env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
 out,err=await p.communicate();return {'ok':p.returncode==0,'text':out.decode(),'error':err.decode(),'returncode':p.returncode}
async def mcp(client,name,kw):
 try:
  r=await client.call_tool(name,{'user_google_email':ACCOUNT,**kw})
  txt='\n'.join(getattr(c,'text','') for c in r.content)
  failed=r.is_error or any(s in txt.lower() for s in ['error executing','authentication required','error:','accounts.google.com'])
  return {'ok':not failed,'text':txt,'error':txt if failed else ''}
 except Exception as e:return {'ok':False,'text':'','error':str(e)}
async def measured(case,tool,fn,trial,expected=None):
 start=time.perf_counter();r=await fn();elapsed=time.perf_counter()-start
 row={'case':case,'tool':tool,'trial':trial,'seconds':round(elapsed,4),'ok':r['ok'],'output_bytes':len(r['text'].encode()),'error':scrub(r['error'])[:1600] if not r['ok'] else ''}
 if expected is not None:row['expected_content_present']=expected in r['text']
 results['samples'].append(row);save();print(case,tool,trial,row['ok'],row['seconds'],flush=True)
 return r
async def check(name,tool,fn,doc,expect=None):
 identity();r=await fn();d=docstate(doc)
 row={'case':name,'tool':tool,'reported_success':r['ok'],'text_after':textof(d),'error':scrub(r['error'])[:1600] if not r['ok'] else ''}
 if expect is not None:row['expected_text']=expect;row['text_matches']=row['text_after'].rstrip('\n')==expect.rstrip('\n')
 row['paragraphs']=[{'text':''.join(e.get('textRun',{}).get('content','') for e in p['paragraph'].get('elements',[])),'style':p['paragraph'].get('paragraphStyle',{}).get('namedStyleType'),'bullet':'bullet' in p['paragraph']} for t in d['tabs'] for p in t.get('documentTab',{}).get('body',{}).get('content',[]) if 'paragraph' in p]
 results['checks'].append(row);save();print('CHECK',name,tool,r['ok'],row.get('text_matches'),flush=True)
 return d
async def main():
 global folder
 identity();folder=created('folder',drive.files().create(body={'name':'Agent tool comparison synthetic fixtures '+datetime.now().strftime('%Y-%m-%d %H%M'),'mimeType':'application/vnd.google-apps.folder'},fields='id').execute()['id'])
 base='Quarterly plan\n'+''.join(f'Item {i:03d}: Keep this sentence unchanged. Budget 1200. Owner Example.\n' for i in range(60))+'Status: DRAFT\n'+''.join(f'PLACEHOLDER_{i:02d}\n' for i in range(10))
 specimens={tool:newdoc(tool+' benchmark',base) for tool in ['gdoc','workspace']}
 for doc in specimens.values():update(doc,[{'updateTextStyle':{'range':{'startIndex':1,'endIndex':15},'textStyle':{'bold':True},'fields':'bold'}}])
 identity();sheet=created('spreadsheet',sheets.spreadsheets().create(body={'properties':{'title':'Comparison synthetic sheet'},'sheets':[{'properties':{'title':t}} for t in ['Data','Other','Third']]}).execute()['spreadsheetId'])
 identity();drive.files().update(fileId=sheet,addParents=folder,fields='id').execute()
 values=[[f'row {i}',str(i),'00123','plain'] for i in range(100)]
 identity();sheets.spreadsheets().values().update(spreadsheetId=sheet,range='Data!A1:D100',valueInputOption='RAW',body={'values':values}).execute()
 csvfile=LOCAL/'rows.csv'
 with csvfile.open('w') as f:csv.writer(f).writerows(values)
 transport=StdioTransport(command=str(Path.home()/'.local/bin/workspace-mcp'),args=['--transport','stdio','--tool-tier','complete','--tools','drive','docs','sheets'],env={'GOOGLE_CLIENT_SECRET_PATH':str(Path.home()/'.config/gdoc/credentials.json'),'WORKSPACE_MCP_CREDENTIALS_DIR':str(Path.home()/'.google_workspace_mcp/credentials'),'WORKSPACE_MCP_LOG_LEVEL':'ERROR'},log_file=open(LOCAL/'mcp.log','w'))
 start=time.perf_counter()
 async with Client(transport) as client:
  names=await client.list_tools();results['startup_seconds']=round(time.perf_counter()-start,4);results['enabled_tools']=len(names)
  # Warm Google service construction and document-awareness state; exclude warmups.
  for tool,doc in specimens.items():
   await (cli(['cat',doc]) if tool=='gdoc' else mcp(client,'get_doc_as_markdown',{'document_id':doc,'include_comments':False}))
  for trial in range(args.trials):
   order=['gdoc','workspace'] if trial%2==0 else ['workspace','gdoc']
   for tool in order:
    doc=specimens[tool]
    await measured('read_doc_4kb',tool,lambda:cli(['cat',doc]) if tool=='gdoc' else mcp(client,'get_doc_as_markdown',{'document_id':doc,'include_comments':False}),trial,'Keep this sentence unchanged')
    await measured('read_with_comments',tool,lambda:cli(['cat',doc,'--comments']) if tool=='gdoc' else mcp(client,'get_doc_as_markdown',{'document_id':doc,'include_comments':True}),trial)
    old,new=('DRAFT','FINAL') if trial%2==0 else ('FINAL','DRAFT')
    identity()
    await measured('replace_plain_phrase',tool,lambda:cli(['edit',doc,old,new,'--all']) if tool=='gdoc' else mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':old,'replace_text':new}),trial)
    native=docstate(doc);assert new in textof(native) and old not in textof(native)
    await measured('read_100_rows',tool,lambda:cli(['cat',sheet,'--tab','Data','--range','A1:D100']) if tool=='gdoc' else mcp(client,'read_sheet_values',{'spreadsheet_id':sheet,'range_name':'Data!A1:D100'}),trial,'row 99')
    identity()
    await measured('write_100_rows',tool,lambda:cli(['cells',sheet,'Data!A1:D100','--file',str(csvfile)]) if tool=='gdoc' else mcp(client,'modify_sheet_values',{'spreadsheet_id':sheet,'range_name':'Data!A1:D100','values':values,'value_input_option':'RAW'}),trial)
    actual=sheets.spreadsheets().values().get(spreadsheetId=sheet,range='Data!A1:D100').execute()['values'];assert actual==values
  # Batch vs ten CLI commands: matched specimens; explicit per-call account checks.
  for tool,doc in specimens.items():
   async def fill():
    if tool=='workspace':return await mcp(client,'batch_update_doc',{'document_id':doc,'operations':[{'type':'find_replace','find_text':f'PLACEHOLDER_{i:02d}','replace_text':f'VALUE_{i:02d}'} for i in range(10)]})
    rr=[]
    for i in range(10):rr.append(await cli(['edit',doc,f'PLACEHOLDER_{i:02d}',f'VALUE_{i:02d}','--all']))
    return {'ok':all(r['ok'] for r in rr),'text':'\n'.join(r['text'] for r in rr),'error':'\n'.join(r['error'] for r in rr)}
   identity();r=await measured('replace_ten_different_phrases',tool,fill,0)
   native=docstate(doc);results['checks'].append({'case':'ten_replacements','tool':tool,'reported_success':r['ok'],'all_replaced':all(f'VALUE_{i:02d}' in textof(native) for i in range(10))})
   await measured('inspect_structure',tool,lambda:cli(['structure',doc]) if tool=='gdoc' else mcp(client,'inspect_doc_structure',{'document_id':doc}),0)
  # Confirm disputed Unicode behavior live on disposable native documents.
  for source in ['İ cat\n','İİ cat\n']:
   for tool in ['gdoc','workspace']:
    doc=newdoc(tool+' unicode find',source)
    await check('unicode_casefold_'+str(source.count('İ')),tool,lambda:cli(['edit',doc,'cat','dog','--all']) if tool=='gdoc' else mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':'cat','replace_text':'dog'}),doc,source.replace('cat','dog'))
  for tool in ['gdoc','workspace']:
   doc=newdoc(tool+' unicode markdown');tab=docstate(doc)['tabs'][0]['tabProperties']['tabId']
   md=LOCAL/'emoji.md';md.write_text('# Plan 😀\n\nNext')
   if tool=='gdoc':assert (await cli(['cat',doc,'--tab',tab]))['ok']
   await check('emoji_markdown',tool,lambda:cli(['write',doc,str(md),'--tab',tab]) if tool=='gdoc' else mcp(client,'manage_doc_tab',{'document_id':doc,'action':'populate_from_markdown','tab_id':tab,'markdown_text':md.read_text()}),doc)
  # Check preservation when changing plain text adjacent to unrelated native bold text.
  for tool in ['gdoc','workspace']:
   doc=newdoc(tool+' style preservation','Keep this bold. Send the draft today.\n')
   update(doc,[{'updateTextStyle':{'range':{'startIndex':1,'endIndex':16},'textStyle':{'bold':True},'fields':'bold'}}])
   d=await check('unrelated_bold',tool,lambda:cli(['edit',doc,'draft','final']) if tool=='gdoc' else mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':'draft','replace_text':'final'}),doc,'Keep this bold. Send the final today.\n')
   runs=d['tabs'][0]['documentTab']['body']['content'][1]['paragraph']['elements']
   results['checks'][-1]['text_runs']=[{'text':e.get('textRun',{}).get('content'),'style':e.get('textRun',{}).get('textStyle')} for e in runs]
  # Compare appending a normal paragraph after a heading.
  for tool in ['gdoc','workspace']:
   doc=newdoc(tool+' paragraph inheritance','Heading\n')
   update(doc,[{'updateParagraphStyle':{'range':{'startIndex':1,'endIndex':9},'paragraphStyle':{'namedStyleType':'HEADING_1'},'fields':'namedStyleType'}}])
   tab=docstate(doc)['tabs'][0]['tabProperties']['tabId'];md=LOCAL/'append.md';md.write_text('Plain paragraph\n')
   if tool=='gdoc':assert (await cli(['cat',doc,'--tab',tab]))['ok']
   await check('append_after_heading',tool,lambda:cli(['insert',doc,str(md),'--tab',tab,'--position','end']) if tool=='gdoc' else mcp(client,'manage_doc_tab',{'document_id':doc,'action':'populate_from_markdown','tab_id':tab,'markdown_text':'Plain paragraph\n','replace_existing':False}),doc)
 results['ended_utc']=datetime.now(timezone.utc).isoformat()
 groups={}
 for row in results['samples']:groups.setdefault((row['case'],row['tool']),[]).append(row)
 results['summary']=[{'case':case,'tool':tool,'n':len(rows),'successes':sum(r['ok'] for r in rows),'median_seconds':round(statistics.median(r['seconds'] for r in rows),4),'min_seconds':min(r['seconds'] for r in rows),'max_seconds':max(r['seconds'] for r in rows),'median_output_bytes':statistics.median(r['output_bytes'] for r in rows)} for (case,tool),rows in groups.items()]
 save();print('DONE',OUT,flush=True)
if __name__=='__main__':asyncio.run(main())
