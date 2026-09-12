"""Resolve harness setup issues and independently check remaining live questions."""
import asyncio,importlib.util,json,os,sys,time
from pathlib import Path
from datetime import datetime,timezone
spec=importlib.util.spec_from_file_location('features',Path(__file__).with_name('live-feature-checks.py'))
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);b=f.b
b.OUT=b.ROOT/'evidence/live-mcp-benchmark.json'
b.results={'started_utc':datetime.now(timezone.utc).isoformat(),'checks':[],'samples':[],'scope':'corrected setup, native oracle, MCP vs MCP','resources_created':len(b.ledger)}
async def main():
 async with b.Client(f.transport()) as client:
  doc=next(x['id'] for x in b.ledger if x['kind']=='workspace benchmark')
  r=await client.call_tool('insert_doc_image',{'user_google_email':b.ACCOUNT,'document_id':doc,'image_source':doc,'index':1},raise_on_error=False)
  txt='\n'.join(getattr(c,'text','') for c in r.content)
  f.record('non_image_source_error_contract','workspace',bool(r.is_error),mcp_is_error=r.is_error,response=b.scrub(txt))
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
  assert (await call('gdoc_cat',{'doc':doc}))['ok']
  for i in range(5):
   await b.measured('read_doc_4kb','gdoc_mcp',lambda:call('gdoc_cat',{'doc':doc}),i,'Keep this sentence unchanged')
   old,new=('DRAFT','FINAL') if i%2==0 else ('FINAL','DRAFT');b.identity()
   r=await b.measured('replace_plain_phrase','gdoc_mcp',lambda:call('gdoc_edit',{'doc':doc,'old_text':old,'new_text':new,'all':True}),i)
   f.record('gdoc_mcp_replace_'+str(i),'gdoc_mcp',r['ok'] and new in b.textof(b.docstate(doc)) and old not in b.textof(b.docstate(doc)))
 b.results['ended_utc']=datetime.now(timezone.utc).isoformat();b.save();print('DONE',flush=True)
if __name__=='__main__':asyncio.run(main())
