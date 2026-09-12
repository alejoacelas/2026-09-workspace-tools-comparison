"""Live differential Unicode matching: pinned gdoc vs native replaceAllText.

Creates exactly two synthetic scratch Docs per invocation, resetting their own
body before each case. No normalization equivalence is assumed. No file deletion,
sharing, real document edits, or collection changes. IDs remain local/ignored.
"""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
CASES=[
 ('ascii_control','Budget draft','DRAFT','control'),
 ('sigma_upper_to_small','Σ','σ','Greek sigma'),
 ('sigma_final_to_small','ς','σ','Greek sigma'),
 ('sigma_word_final','ΟΣ','οσ','Greek sigma'),
 ('sigma_final_to_upper','ς','Σ','Greek sigma'),
 ('sharp_s_capital','ẞ','ß','German sharp S'),
 ('sharp_s_expansion','Straße','STRASSE','German sharp S'),
 ('kelvin_sign','Kelvin','kelvin','compatibility letter'),
 ('long_s','ſale','sale','compatibility letter'),
 ('micro_sign','µg','μg','compatibility letter'),
 ('dotless_i','ı','I','Turkish I'),
 ('dotted_i','İ','i','known Turkish-I expansion family'),
 ('dotted_i_before_target','İ cat sat','cat','known Turkish-I indexing damage'),
 ('composed_name','José','JOSÉ','accent case control'),
 ('decomposed_name','Jose\u0301','JOSÉ','normalization hypothesis'),
 ('composed_to_decomposed','José','Jose\u0301','normalization hypothesis'),
 ('curly_apostrophe','Owner’s budget',"Owner's",'literal punctuation control'),
 ('nbsp','Budget\u00a0draft','Budget draft','literal whitespace control'),
 ('cyrillic_control','План','ПЛАН','control'),
 ('ascii_nonmatch','Budget draft','absent','nonmatch control'),
 ('sigma_exact_character','ΟΣ','Σ','Greek sigma exact-character counterexample','X'),
 ('sigma_office_prefix','Budget Σ','Σ','Greek sigma exact-character control','X'),
]
def body(doc):return b.state(doc)['tabs'][0]['documentTab']['body']['content']
def text(doc):return ''.join(e.get('textRun',{}).get('content','') for p in body(doc) for e in p.get('paragraph',{}).get('elements',[]))
def reset(doc,tab,source):
 content=body(doc);end=content[-1]['endIndex'];requests=[]
 if end>2:requests.append({'deleteContentRange':{'range':{'startIndex':1,'endIndex':end-1,'tabId':tab}}})
 requests.append({'insertText':{'location':{'index':1,'tabId':tab},'text':source}})
 b.update(doc,requests)
resume='--resume' in sys.argv
docs=json.loads((b.LOCAL/'r2-unicode-ledger.json').read_text())['documents'] if resume else {tool:b.new('Synthetic Unicode matching oracle '+tool) for tool in ['gdoc','google']};tabs={tool:b.state(doc)['tabs'][0]['tabProperties']['tabId'] for tool,doc in docs.items()};b.save('r2-unicode-ledger.json',{'documents':docs,'tabs':tabs})
results={'gdoc_revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','replacement':'MATCH','case_sensitive':False,'oracle':'actual native Google replaceAllText result, not assumed Unicode normalization','cases':[]}
if resume:results=json.loads((b.ROOT/'hunt/round2/unicode-matching.json').read_text())
private={b.ACCOUNT:'PERSON_EMAIL',**{v:'DOC' for v in docs.values()},**{v:'TAB' for v in tabs.values()}}
def clean(s):
 for raw,replacement in sorted(private.items(),key=lambda x:-len(x[0])):s=s.replace(raw,replacement)
 return s.replace(str(b.ROOT),'PROJECT')
for case in CASES:
 name,source,find,family,*override=case
 replacement=override[0] if override else 'MATCH'
 if resume and any(row['case']==name for row in results['cases']):continue
 for tool in ['gdoc','google']:reset(docs[tool],tabs[tool],source)
 before={tool:text(doc) for tool,doc in docs.items()}
 assert before['gdoc']==before['google']==source+'\n',before
 r=b.cli(['edit',docs['gdoc'],find,replacement,'--all','--tab',tabs['gdoc']])
 native=b.update(docs['google'],[{'replaceAllText':{'containsText':{'text':find,'matchCase':False},'replaceText':replacement,'tabsCriteria':{'tabIds':[tabs['google']]}}}])
 after={tool:text(doc) for tool,doc in docs.items()}
 row={'case':name,'family':family,'source':source,'find':find,'replacement':replacement,'before':before,'gdoc':{'returncode':r['returncode'],'stdout':clean(r['stdout']),'stderr':clean('\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:'))),'after':after['gdoc']},'google':{'occurrences_changed':sum(x.get('replaceAllText',{}).get('occurrencesChanged',0) for x in native.get('replies',[])),'after':after['google']},'same_final_text':after['gdoc']==after['google']}
 row['source_codepoints']=['U+%04X'%ord(c) for c in source]
 row['find_codepoints']=['U+%04X'%ord(c) for c in find]
 results['cases'].append(row);(b.ROOT/'hunt/round2/unicode-matching.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
 b.save('r2-unicode-'+name+'-gdoc.json',b.state(docs['gdoc']));b.save('r2-unicode-'+name+'-google.json',b.state(docs['google']))
 print(name,'gdoc_rc',r['returncode'],'native_matches',row['google']['occurrences_changed'],'same',row['same_final_text'],repr(after['gdoc']),repr(after['google']),flush=True)
