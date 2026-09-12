"""Fresh independent confirmation of Greek matching and logical TSV records."""
import csv,io,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
id=b.new('Synthetic independent Greek match');tab=b.state(id)['tabs'][0]['tabProperties']['tabId'];b.save('r2-independent-greek-ledger.json',{'id':id})
b.update(id,[{'insertText':{'location':{'index':1,'tabId':tab},'text':'ΟΣ'}}]);assert b.cli(['cat',id,'--tab',tab])['returncode']==0
r=b.cli(['edit',id,'Σ','X','--all','--tab',tab]);assert r['returncode']==3 and 'no match found' in r['stderr']
from confirm import text
assert text(b.state(id)['tabs']).strip()=='ΟΣ'
r2=b.update(id,[{'replaceAllText':{'containsText':{'text':'Σ','matchCase':False},'replaceText':'X','tabsCriteria':{'tabIds':[tab]}}}]);assert r2['replies'][0]['replaceAllText']['occurrencesChanged']==1 and text(b.state(id)['tabs']).strip()=='ΟX'
l=json.loads((b.LOCAL/'r2-review-ledger.json').read_text());raw=b.cli(['comments',l['doc'],'--plain']);assert raw['returncode']==0
records=list(csv.reader(io.StringIO(raw['stdout']),delimiter='\t'));assert len(records)==2 and [len(x) for x in records]==[5,2]
result={'greek':{'source':'ΟΣ','find':'Σ','replacement':'X','gdoc_returncode':3,'gdoc_after':'ΟΣ','native_google_matches':1,'native_google_after':'ΟX'},'comments_plain':{'returncode':0,'parsed_records':2,'fields_per_record':[5,2]}}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');print('Greek exact-character failure and logical TSV record corruption independently confirmed')
