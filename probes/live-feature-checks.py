"""Additional live checks; reuses benchmark helpers and the existing synthetic folder.
Run after live-benchmark.py, with the same explicit --account. No real office files.
"""
import asyncio, importlib.util, json, os, re, sys, time
from pathlib import Path
from datetime import datetime, timezone
spec=importlib.util.spec_from_file_location('bench',Path(__file__).with_name('live-benchmark.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.OUT=b.ROOT/'evidence/live-feature-checks.json'
b.results={'started_utc':datetime.now(timezone.utc).isoformat(),'scope':'synthetic fixtures, additional native state checks; not a representative reliability rate','samples':[],'checks':[],'resources_created':0}
b.ledger=json.loads((b.LOCAL/'ledger.json').read_text());b.folder=b.ledger[0]['id']
def record(name,tool,ok,**details):
 b.results['checks'].append({'case':name,'tool':tool,'pass':ok,**details});b.save();print(name,tool,ok,flush=True)
def transport():
 return b.StdioTransport(command=str(Path.home()/'.local/bin/workspace-mcp'),args=['--transport','stdio','--tool-tier','complete','--tools','drive','docs','sheets'],env={'GOOGLE_CLIENT_SECRET_PATH':str(Path.home()/'.config/gdoc/credentials.json'),'WORKSPACE_MCP_CREDENTIALS_DIR':str(Path.home()/'.google_workspace_mcp/credentials'),'WORKSPACE_MCP_LOG_LEVEL':'ERROR'},log_file=open(b.LOCAL/'features-mcp.log','w'))
def runs(d):
 return [{'text':e.get('textRun',{}).get('content'),'style':e.get('textRun',{}).get('textStyle')} for t in d['tabs'] for p in t.get('documentTab',{}).get('body',{}).get('content',[]) if 'paragraph' in p for e in p['paragraph'].get('elements',[])]
async def main():
 async with b.Client(transport()) as client:
  # Correctly establish a read baseline and explicitly choose append-at-end.
  for name,source,md in [('emoji_markdown','', '# Plan 😀\n\nNext'),('paragraph_after_heading','Heading\n','Plain paragraph\n'),('nested_lists','','- Parent\n  - Child\n- Peer'),('markdown_links','','[Policy](https://example.com/Policy_(2026))'),('intraword_underscore','','office_budget_total')]:
   for tool in ['gdoc','workspace']:
    doc=b.newdoc(tool+' '+name,source);tab=b.docstate(doc)['tabs'][0]['tabProperties']['tabId']
    if source:b.update(doc,[{'updateParagraphStyle':{'range':{'startIndex':1,'endIndex':9},'paragraphStyle':{'namedStyleType':'HEADING_1'},'fields':'namedStyleType'}}])
    mdfile=b.LOCAL/'feature.md';mdfile.write_text(md)
    if tool=='gdoc':
     read=await b.cli(['cat',doc,'--tab',tab]);assert read['ok'],read['error']
    async def action():
     if tool=='workspace':return await b.mcp(client,'manage_doc_tab',{'document_id':doc,'action':'populate_from_markdown','tab_id':tab,'markdown_text':md,'replace_existing':not bool(source)})
     return await b.cli((['insert',doc,str(mdfile),'--tab',tab,'--position','end'] if source else ['write',doc,str(mdfile),'--tab',tab]))
    d=await b.check(name,tool,action,doc)
    b.results['checks'][-1]['text_runs']=runs(d)
    b.results['checks'][-1]['native_body']=d['tabs'][0]['documentTab']['body'];b.save()
  # A longer suffix makes the Unicode wrong-range bug visibly distinguishable from newline rejection.
  for tool in ['gdoc','workspace']:
   doc=b.newdoc(tool+' casefold suffix','İ cat sat\n')
   await b.check('casefold_visible_corruption',tool,lambda:b.cli(['edit',doc,'cat','dog','--all']) if tool=='gdoc' else b.mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':'cat','replace_text':'dog'}),doc,'İ dog sat\n')
  # Real comment payload: create, read, reply, resolve, and gdoc-only reopen.
  for tool in ['gdoc','workspace']:
   doc=b.newdoc(tool+' collaboration','Review this synthetic sentence.\n')
   b.identity();r=await (b.cli(['comment',doc,'Please verify the synthetic total.']) if tool=='gdoc' else b.mcp(client,'manage_document_comment',{'document_id':doc,'action':'create','comment_content':'Please verify the synthetic total.'}))
   threads=b.drive.comments().list(fileId=doc,fields='comments(id,content,resolved)').execute().get('comments',[])
   record('create_comment',tool,r['ok'] and len(threads)==1 and threads[0]['content']=='Please verify the synthetic total.',error=b.scrub(r['error'])[:600] if not r['ok'] else '')
   if not threads:continue
   cid=threads[0]['id']
   for trial in range(3):await b.measured('read_with_one_comment',tool,lambda:b.cli(['cat',doc,'--comments']) if tool=='gdoc' else b.mcp(client,'get_doc_as_markdown',{'document_id':doc,'include_comments':True}),trial,'Please verify the synthetic total.')
   b.identity();r=await (b.cli(['reply',doc,cid,'Confirmed synthetic total.']) if tool=='gdoc' else b.mcp(client,'manage_document_comment',{'document_id':doc,'action':'reply','comment_id':cid,'reply_content':'Confirmed synthetic total.'}))
   thread=b.drive.comments().get(fileId=doc,commentId=cid,fields='replies(content),resolved').execute();record('reply_comment',tool,r['ok'] and any(x['content']=='Confirmed synthetic total.' for x in thread.get('replies',[])))
   b.identity();r=await (b.cli(['resolve',doc,cid]) if tool=='gdoc' else b.mcp(client,'manage_document_comment',{'document_id':doc,'action':'resolve','comment_id':cid}))
   thread=b.drive.comments().get(fileId=doc,commentId=cid,fields='resolved').execute();record('resolve_comment',tool,r['ok'] and thread.get('resolved') is True)
   if tool=='gdoc':
    b.identity();r=await b.cli(['reopen',doc,cid]);thread=b.drive.comments().get(fileId=doc,commentId=cid,fields='resolved').execute();record('reopen_comment',tool,r['ok'] and not thread.get('resolved'))
  # Change data on every measured write: preloaded values cannot satisfy the postcondition.
  sheet=next(x['id'] for x in b.ledger if x['kind']=='spreadsheet')
  for trial in range(3):
   for tool in (['gdoc','workspace'] if trial%2==0 else ['workspace','gdoc']):
    values=[[f'{tool}-{trial}-{i}',str(i),'00123','plain'] for i in range(100)]
    file=b.LOCAL/'changed-rows.csv'
    with file.open('w') as f:b.csv.writer(f).writerows(values)
    before=b.sheets.spreadsheets().values().get(spreadsheetId=sheet,range='Data!A1:D100').execute().get('values');assert before!=values
    b.identity();r=await b.measured('write_changed_100_rows',tool,lambda:b.cli(['cells',sheet,'Data!A1:D100','--file',str(file)]) if tool=='gdoc' else b.mcp(client,'modify_sheet_values',{'spreadsheet_id':sheet,'range_name':'Data!A1:D100','values':values,'value_input_option':'RAW'}),trial)
    after=b.sheets.spreadsheets().values().get(spreadsheetId=sheet,range='Data!A1:D100').execute().get('values');record('changed_cells_'+str(trial),tool,r['ok'] and after==values)
  # Native table phrase replacement, with unrelated label and table shape preserved.
  md='| Label | Value |\n| --- | --- |\n| Status | DRAFT |\n'
  file=b.LOCAL/'table.md';file.write_text(md)
  for tool in ['gdoc','workspace']:
   b.identity()
   if tool=='gdoc':
    r=await b.cli(['new','Comparison synthetic table','--file',str(file),'--folder',b.folder,'--json']);doc=json.loads(r['text'])['id']
   else:
    r=await b.mcp(client,'import_to_google_doc',{'file_name':'Comparison synthetic table.md','content':md,'folder_id':b.folder});match=re.search(r'document/d/([\w-]+)',r['text']);assert match,r;doc=match.group(1)
   b.created(tool+' native table',doc)
   before=b.docstate(doc);beforebody=before['tabs'][0]['documentTab']['body']['content'];assert any('table' in x for x in beforebody)
   b.identity();r=await (b.cli(['edit',doc,'DRAFT','FINAL']) if tool=='gdoc' else b.mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':'DRAFT','replace_text':'FINAL'}))
   d=b.docstate(doc);tables=[x['table'] for x in d['tabs'][0]['documentTab']['body']['content'] if 'table' in x]
   record('native_table_phrase_edit',tool,r['ok'] and 'FINAL' in b.textof(d) and len(tables)==1 and tables[0]['rows']==2 and tables[0]['columns']==2,text_after=b.textof(d))
  # gdoc-only review/export paths: smoke checks, no unsupported comparison forced.
  doc=next(x['id'] for x in b.ledger if x['kind']=='gdoc benchmark')
  for name,argv in [('revisions',['revisions',doc]),('toc',['toc',doc]),('info',['info',doc]),('tabs',['tabs',doc])]:
   r=await b.cli(argv);record(name,'gdoc',r['ok'],output_bytes=len(r['text'].encode()))
  target=b.LOCAL/'export.pdf';r=await b.cli(['export',doc,'--out',str(target)]);record('export_pdf','gdoc',r['ok'] and target.exists() and target.read_bytes().startswith(b'%PDF'))
 b.results['ended_utc']=datetime.now(timezone.utc).isoformat();b.save();print('DONE',flush=True)
if __name__=='__main__':asyncio.run(main())
