"""Live synthetic native nested-table/list read check. Never shares/deletes."""
import io,json
import live as b
from googleapiclient.http import MediaIoBaseUpload
HTML='''<!doctype html><html><body><h1>Export fidelity specimen</h1><table border="1"><tr><td>Outer cell<table border="1"><tr><td>Materials</td><td>475</td></tr></table></td></tr></table><p>Numbered procedure</p><ol start="7"><li>Review budget</li><li>Approve purchase</li></ol></body></html>'''
def walk(x,depth=0):
 if isinstance(x,dict):
  if 'table' in x:
   yield {'depth':depth,'rows':x['table'].get('rows'),'columns':x['table'].get('columns')}
   yield from walk(x['table'],depth+1)
  else:
   for v in x.values():yield from walk(v,depth)
 elif isinstance(x,list):
  for v in x:yield from walk(v,depth)
def text(x):
 if isinstance(x,dict):
  if 'textRun' in x:return x['textRun'].get('content','')
  return ''.join(text(v) for v in x.values())
 if isinstance(x,list):return ''.join(text(v) for v in x)
 return ''
def scrub(t,id,tab):return t.replace(id,'DOC').replace(tab,'TAB').replace(b.ACCOUNT,'PERSONAL').replace(str(b.ROOT),'PROJECT')
b.identity()
resource=b.drive.files().create(body={'name':'Synthetic gdoc export nesting and list start','mimeType':'application/vnd.google-apps.document'},media_body=MediaIoBaseUpload(io.BytesIO(HTML.encode()),mimetype='text/html',resumable=False),fields='id').execute()['id']
b.save('export-extra-ledger.json',{'document_id':resource,'html':HTML})
d=b.state(resource);b.save('export-extra-native.json',d)
tab=d['tabs'][0]['tabProperties']['tabId'];native=d['tabs'][0]['documentTab'];tables=list(walk(native['body']))
results={'gdoc_revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','input_html':HTML,'native_tables':tables,'native_text':text(native['body']),'native_lists':native.get('lists',{}),'native_nested_table_confirmed':any(t['depth']>=1 for t in tables),'reads':[]}
# List IDs are generated, not meaningful. Publish their values only.
results['native_lists']=list(results['native_lists'].values())
for name,argv in [('default',['cat',resource]),('selected_tab',['cat',resource,'--tab',tab])]:
 r=b.cli(argv)
 results['reads'].append({'route':name,'returncode':r['returncode'],'stdout':scrub(r['stdout'],resource,tab),'stderr':scrub(r['stderr'],resource,tab),'contains_inner_materials':'Materials' in r['stdout'],'contains_inner_475':'475' in r['stdout']})
(b.ROOT/'hunt/export-extra-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
