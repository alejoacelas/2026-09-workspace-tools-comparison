"""Resolve harness setup issues and independently check remaining live questions."""
import asyncio,importlib.util,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
spec=importlib.util.spec_from_file_location('features',Path(__file__).with_name('live-feature-checks.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);b=f.b
b.OUT=b.ROOT/'evidence/live-followups.json'
b.results={'started_utc':datetime.now(timezone.utc).isoformat(),'checks':[],'samples':[],'scope':'corrected setup, native oracle, MCP vs MCP','resources_created':len(b.ledger)}
async def main():
 async with b.Client(f.transport()) as client:
  doc=next(x['id'] for x in b.ledger if x['kind']=='gdoc paragraph_after_heading')
  tab=b.docstate(doc)['tabs'][0]['tabProperties']['tabId'];md=b.LOCAL/'followup.md';md.write_text('Plain paragraph\n')
  assert (await b.cli(['cat',doc,'--tab',tab]))['ok']
  await b.check('append_after_heading_corrected_baseline','gdoc',lambda:b.cli(['insert',doc,str(md),'--tab',tab,'--position','end']),doc)
  doc=next(x['id'] for x in b.ledger if x['kind']=='workspace collaboration')
  cid=b.drive.comments().list(fileId=doc,fields='comments(id)').execute()['comments'][0]['id']
  b.identity();r=await b.mcp(client,'manage_document_comment',{'document_id':doc,'action':'reply','comment_id':cid,'comment_content':'Confirmed synthetic total.'})
  replies=b.drive.comments().get(fileId=doc,commentId=cid,fields='replies(content)').execute().get('replies',[])
  f.record('reply_comment_correct_schema','workspace',r['ok'] and any(x['content']=='Confirmed synthetic total.' for x in replies))
  # ASCII control separates heading inheritance from the emoji index bug.
  for tool in ['gdoc','workspace']:
   doc=b.newdoc(tool+' ascii heading');tab=b.docstate(doc)['tabs'][0]['tabProperties']['tabId'];md.write_text('# Plan\n\nNext')
   if tool=='gdoc':assert (await b.cli(['cat',doc,'--tab',tab]))['ok']
   await b.check('ascii_heading_body',tool,lambda:b.cli(['write',doc,str(md),'--tab',tab]) if tool=='gdoc' else b.mcp(client,'manage_doc_tab',{'document_id':doc,'action':'populate_from_markdown','tab_id':tab,'markdown_text':md.read_text()}),doc)
  # Native API reference sends one bullet operation for the whole list.
  doc=b.newdoc('native nested-list oracle','Parent\n\tChild\nPeer\n')
  b.update(doc,[{'createParagraphBullets':{'range':{'startIndex':1,'endIndex':19},'bulletPreset':'BULLET_DISC_CIRCLE_SQUARE'}}])
  d=b.docstate(doc);paras=[x['paragraph'] for x in d['tabs'][0]['documentTab']['body']['content'] if 'paragraph' in x]
  f.record('native_grouped_bullets','google_api',paras[1].get('bullet',{}).get('nestingLevel')==1,paragraphs=paras)
  # Tab isolation through both exposed interfaces.
  for tool in ['gdoc','workspace']:
   doc=b.newdoc(tool+' tab isolation','Status: DRAFT\n')
   b.update(doc,[{'addDocumentTab':{'tabProperties':{'title':'Second','index':1}}}])
   tabs=b.docstate(doc)['tabs'];second=tabs[1]['tabProperties']['tabId']
   b.update(doc,[{'insertText':{'location':{'index':1,'tabId':second},'text':'Status: DRAFT\n'}}])
   b.identity();r=await (b.cli(['edit',doc,'DRAFT','FINAL','--tab',second]) if tool=='gdoc' else b.mcp(client,'find_and_replace_doc',{'document_id':doc,'find_text':'DRAFT','replace_text':'FINAL','tab_id':second}))
   d=b.docstate(doc);texts=[b.textof({'tabs':[t]}) for t in d['tabs']]
   f.record('selected_tab_replace',tool,r['ok'] and 'DRAFT' in texts[0] and 'FINAL' in texts[1],tab_texts=texts)
   r=await (b.cli(['cat',doc,'--all-tabs']) if tool=='gdoc' else b.mcp(client,'get_doc_as_markdown',{'document_id':doc,'include_comments':False}))
   f.record('read_all_doc_tabs',tool,r['ok'] and 'DRAFT' in r['text'] and 'FINAL' in r['text'])
  # Direct Google scopes/transport don't require a false string-success claim.
  r=await client.call_tool('insert_doc_image',{'user_google_email':b.ACCOUNT,'document_id':doc,'image_source':'not-a-url','index':1})
  txt='\n'.join(getattr(c,'text','') for c in r.content)
  f.record('invalid_image_error_contract','workspace',bool(r.is_error),mcp_is_error=r.is_error,response=b.scrub(txt))
 # Same-process transport comparison: gdoc's actual stdio MCP wrapper.
 transport=b.StdioTransport(command=str(b.ROOT/'repos/gdoc/.venv/bin/python'),args=['-m','gdoc','mcp','--account',b.ACCOUNT],cwd=str(b.ROOT/'repos/gdoc'),env={**os.environ,'GDOC_AUTO_UPDATE':'0','PYTHONPATH':str(b.ROOT/'repos/gdoc')},log_file=open(b.LOCAL/'gdoc-mcp.log','w'))
 start=time.perf_counter()
 async with b.Client(transport) as client:
  ts=await client.list_tools();b.results['gdoc_mcp_startup_seconds']=round(time.perf_counter()-start,4);b.results['gdoc_mcp_tools']=len(ts)
  doc=b.newdoc('gdoc MCP benchmark','Quarterly plan\n'+''.join(f'Item {i:03d}: Keep this sentence unchanged. Budget 1200. Owner Example.\n' for i in range(60))+'Status: DRAFT\n'+''.join(f'VALUE_{i:02d}\n' for i in range(10)))
  async def call(name,kw):
   try:
    r=await client.call_tool(name,{'account':b.ACCOUNT,**kw});txt='\n'.join(getattr(c,'text','') for c in r.content)
    return {'ok':not r.is_error,'text':txt,'error':txt if r.is_error else ''}
   except Exception as e:return {'ok':False,'text':'','error':str(e)}
  await call('gdoc_cat',{'doc':doc})
  for i in range(5):
   await b.measured('read_doc_4kb','gdoc_mcp',lambda:call('gdoc_cat',{'doc':doc}),i,'Keep this sentence unchanged')
   old,new=('DRAFT','FINAL') if i%2==0 else ('FINAL','DRAFT');b.identity()
   r=await b.measured('replace_plain_phrase','gdoc_mcp',lambda:call('gdoc_edit',{'doc':doc,'old_text':old,'new_text':new,'all':True}),i)
   f.record('gdoc_mcp_replace_'+str(i),'gdoc_mcp',r['ok'] and new in b.textof(b.docstate(doc)))
 b.results['ended_utc']=datetime.now(timezone.utc).isoformat();b.save();print('DONE',flush=True)
if __name__=='__main__':asyncio.run(main())
