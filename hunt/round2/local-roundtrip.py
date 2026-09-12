"""Live pull/local edit/push controls on synthetic plain documents only."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
from gdoc.frontmatter import parse_frontmatter,add_frontmatter
folder=b.LOCAL/'r2-local-files';folder.mkdir(exist_ok=True);folder.chmod(0o700)
ledger={};results=[]
def create(key,title,text):
 doc=b.new(title);ledger[key]=doc;b.save('r2-local-ledger.json',ledger);b.update(doc,[{'insertText':{'location':{'index':1},'text':text}}]);return doc
def state(doc):
 d=b.state(doc);out=[]
 for t in d['tabs']:
  out.append({'tab_id':t['tabProperties']['tabId'],'title':t['tabProperties']['title'],'text':''.join(e.get('textRun',{}).get('content','') for p in t['documentTab']['body']['content'] for e in p.get('paragraph',{}).get('elements',[]))})
 return out
def body(doc):return state(doc)[0]['text'].rstrip('\n')
def title(doc):return b.drive.files().get(fileId=doc,fields='name').execute()['name']
def clean(s):
 for k,v in ledger.items():s=s.replace(v,k.upper())
 return s.replace(b.ACCOUNT,'PERSONAL').replace(str(folder),'LOCAL_FILES').replace(str(b.ROOT),'PROJECT')
def call(args):return b.cli(args)
def save(case,r,ok,**detail):
 results.append({'case':case,'returncode':r['returncode'],'passed':bool(ok),'stdout':clean(r['stdout']),'stderr':clean('\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:'))),**detail})
 (b.ROOT/'hunt/round2/local-roundtrip.json').write_text(json.dumps({'revision':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','scope':'pull/local-edit/push; plain synthetic Docs; tabbed doc safety refusal','cases':results},ensure_ascii=False,indent=2)+'\n');print(case,ok,r['returncode'],flush=True)
def pull(doc,path):
 r=call(['pull',doc,str(path)]);assert r['returncode']==0,r;path.chmod(0o600);return r
def edited(path,old,new):
 s=path.read_text();assert old in s;s=s.replace(old,new);path.write_text(s);path.chmod(0o600)
a=create('source_a','Budget notes','Status draft.\n');btitle="Director's notes: Plan (Σ) #1";other=create('source_b',btitle,'SIBLING KEEP.\n')
f=folder/'standard.md';r=pull(a,f);meta,content=parse_frontmatter(f.read_text());save('pull_metadata_standard',r,meta.get('gdoc')==a and meta.get('title')=='Budget notes' and 'Status draft.' in content)
before=body(a);r=call(['push',str(f)]);save('unchanged_plain_push',r,r['returncode']==0 and body(a)==before and title(a)=='Budget notes',remote_text=body(a),scope_note='Content check only; no claim of zero-write no-op or preservation of rich structure')
r=pull(a,f);edited(f,'Status draft.','Status final.');r=call(['push',str(f)]);save('plain_word_edit_push',r,r['returncode']==0 and body(a)=='Status final.' and body(other)=='SIBLING KEEP.',remote_text=body(a))
f2=folder/"Owner's notes (Σ) résumé.md";r=pull(other,f2);meta,content=parse_frontmatter(f2.read_text());save('punctuation_title_and_local_filename',r,meta.get('gdoc')==other and meta.get('title')==btitle and 'SIBLING KEEP.' in content,local_filename=f2.name,metadata_title=meta.get('title'))
# Name the local file after a different remote document; frontmatter must win.
pull(a,f);renamed=folder/(btitle+'.md');renamed.write_text(f.read_text());renamed.chmod(0o600);edited(renamed,'Status final.','Status approved.');r=call(['push',str(renamed)]);save('renamed_local_file_keeps_doc_binding',r,r['returncode']==0 and body(a)=='Status approved.' and body(other)=='SIBLING KEEP.',source_text=body(a),other_text=body(other))
pull(a,f);meta,content=parse_frontmatter(f.read_text());meta['title']='Local descriptive title only';f.write_text(add_frontmatter(content.replace('approved','ready'),meta));f.chmod(0o600);r=call(['push',str(f)]);save('title_metadata_does_not_retarget_or_rename',r,r['returncode']==0 and body(a)=='Status ready.' and title(a)=='Budget notes' and body(other)=='SIBLING KEEP.',remote_title=title(a),remote_text=body(a))
pull(a,f);s=f.read_text().replace('Status ready.','Status complete.');f.write_bytes(s.replace('\n','\r\n').encode());f.chmod(0o600);r=call(['push',str(f)]);save('crlf_local_file_word_edit',r,r['returncode']==0 and body(a)=='Status complete.',remote_text=body(a))
dash=folder/'--draft Σ.md';pull(a,dash);edited(dash,'Status complete.','Status checked.');r=call(['push',str(dash)]);save('leading_dash_filename_via_absolute_path',r,r['returncode']==0 and body(a)=='Status checked.',local_filename=dash.name,remote_text=body(a))
multi=create('multi','Synthetic local tab binding','FIRST KEEP.\n');b.update(multi,[{'addDocumentTab':{'tabProperties':{'title':'Second','index':1}}}]);tabs=state(multi);second=tabs[1]['tab_id'];ledger['second_tab']=second;b.save('r2-local-ledger.json',ledger);b.update(multi,[{'insertText':{'location':{'index':1,'tabId':second},'text':'SECOND draft.\n'}}]);multi_before=state(multi);local=folder/'selected-tab-link.md'
r=pull('https://docs.google.com/document/d/'+multi+'/edit?tab='+second,local);meta,content=parse_frontmatter(local.read_text());save('tab_url_pull_is_document_bound',r,meta.get('gdoc')==multi and 'tab' not in meta,metadata_keys=sorted(meta),pulled_body=clean(content),scope_note='pull has no --tab argument; URL query does not become a tab-bound push contract')
meta,content=parse_frontmatter(local.read_text());local.write_text(add_frontmatter(content+'\nRequested local addition.\n',meta));local.chmod(0o600);r=call(['push',str(local)]);multi_after=state(multi);save('multi_tab_push_refuses_preserves_siblings',r,r['returncode']==3 and 'would collapse' in r['stderr'] and multi_after==multi_before,tab_count_before=len(multi_before),tab_count_after=len(multi_after),texts_before=[x['text'] for x in multi_before],texts_after=[x['text'] for x in multi_after])
