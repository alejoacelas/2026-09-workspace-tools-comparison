"""Personal synthetic fixtures; local-only IDs. Never shares or deletes resources."""
import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'repos/gdoc'))
from gdoc.auth import get_credentials
from googleapiclient.discovery import build
ACCOUNT='alejoacelas@gmail.com'
LOCAL=ROOT/'.local-hunt'; LOCAL.mkdir(exist_ok=True); LOCAL.chmod(0o700)
creds=get_credentials(ACCOUNT)
drive=build('drive','v3',credentials=creds); docs=build('docs','v1',credentials=creds)
def identity():
    assert drive.about().get(fields='user(emailAddress)').execute()['user']['emailAddress']==ACCOUNT

def save(name,obj):
    p=LOCAL/name;p.write_text(json.dumps(obj,indent=2));p.chmod(0o600)
def cli(args):
    identity()
    p=subprocess.run([str(ROOT/'repos/gdoc/.venv/bin/python'),'-m','gdoc',*args,'--account',ACCOUNT],env={**os.environ,'GDOC_AUTO_UPDATE':'0','PYTHONPATH':str(ROOT/'repos/gdoc')},cwd=ROOT,text=True,capture_output=True)
    return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def state(id): return docs.documents().get(documentId=id,includeTabsContent=True).execute()
def update(id,requests):
    identity(); before=state(id)
    return docs.documents().batchUpdate(documentId=id,body={'writeControl':{'requiredRevisionId':before['revisionId']},'requests':requests}).execute()
def new(label):
    r=cli(['new',label,'--json','--paged']); assert r['returncode']==0,r
    obj=json.loads(r['stdout']); return obj.get('id',obj.get('documentId'))
if __name__=='__main__':
    identity()
    id=json.loads((LOCAL/'collection.json').read_text())['id'] if (LOCAL/'collection.json').exists() else new('gdoc bug hunt — confirmed cases')
    assert id
    d=state(id);tab=d['tabs'][0]['tabProperties']['tabId']
    save('collection.json',{'id':id,'guide_tab':tab,'cases':{}})
    guide='gdoc bug hunt — confirmed cases\nParallel testing of everyday document conversions\n\nThis collection is being populated as cases are confirmed. Each finding has its own tab with a Before / Expected / Observed diagram, a short explanation, and reproduction commands.\n\nEvidence labels distinguish live Google Docs failures from offline converter failures. Illustrations are reconstructed from synthetic test data, not screenshots. Existing campaign families are identified separately from additional regressions.\n\nTarget: public gdoc v0.21.0, commit dbfa4c34. The native Markdown writer is tested separately from whole-document Drive import; they use different converters.\n'
    update(id,[{'insertText':{'location':{'index':1,'tabId':tab},'text':guide}}])
    print('https://docs.google.com/document/d/'+id+'/edit')
