"""Hold gdoc text/styles fixed; compare per-item versus grouped native bullet requests."""
import importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('features',Path(__file__).with_name('live-feature-checks.py'));f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);b=f.b
b.OUT=b.ROOT/'evidence/live-list-oracle.json';b.results={'checks':[],'samples':[],'scope':'native request isolation; not a patched gdoc build','resources_created':len(b.ledger)}
source=json.loads((b.ROOT/'evidence/nested-list-crosscheck.json').read_text())[0]['complete_writer_batches'][0]['requests']
for variant in ['per_item','grouped']:
 doc=b.newdoc('native list isolate '+variant);tab=b.docstate(doc)['tabs'][0]['tabProperties']['tabId']
 requests=json.loads(json.dumps(source).replace('probe-tab',tab))
 if variant=='grouped':
  requests=[r for r in requests if 'createParagraphBullets' not in r]+[{'createParagraphBullets':{'range':{'startIndex':1,'endIndex':19,'tabId':tab},'bulletPreset':'BULLET_DISC_CIRCLE_SQUARE'}}]
 b.update(doc,requests)
 d=b.docstate(doc);ps=[x['paragraph'] for x in d['tabs'][0]['documentTab']['body']['content'] if 'paragraph' in x]
 f.record('same_text_style_'+variant,'google_api',ps[1].get('bullet',{}).get('nestingLevel')==1,requests=requests,paragraphs=ps)
print('DONE')
