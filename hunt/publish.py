"""Append reviewed cases to the explicitly selected personal Google collection.
Native targeted requests avoid relying on the converters being evaluated.
Images are public synthetic PNGs; the Google Doc is not shared by this script.
"""
import json,subprocess,sys
from pathlib import Path
import live as b
ROOT=Path(__file__).resolve().parent
COMMIT=sys.argv[1]
BASE='https://raw.githubusercontent.com/alejoacelas/2026-09-workspace-tools-comparison/'+COMMIT+'/hunt/figures/'
def u(s):return len(s.encode('utf-16-le'))//2
def main():
 collection=json.loads((b.LOCAL/'collection.json').read_text());id=collection['id']
 for c in json.loads((ROOT/'confirmed.json').read_text()):
  if c['id'] in collection['cases']:continue
  assert not any(t['tabProperties']['title']==c['short']+' '+c['title'] for t in b.state(id)['tabs']), 'Unrecorded existing case tab: inspect before retrying'
  r=b.cli(['add-tab',id,c['short']+' '+c['title'],'--json']);assert r['returncode']==0,r
  tab=json.loads(r['stdout'])['id']
  top=c['short']+' · '+c['title']+'\n'+c['intent']+'\n'
  tail='\nBug. '+c['bug']+'\nCommands\n'+c['commands']+'\n'+c.get('setup','Setup: use a separate blank tab; specimen.md contains the exact Markdown shown above.')+'\nEvidence: live native readback; command returned success. '+c['novelty']+'\nSource and reproduction evidence\n'
  text=top+'\n'+tail
  rg={'tabId':tab,'startIndex':1,'endIndex':1+u(text)}
  req=[{'insertText':{'location':{'index':1,'tabId':tab},'text':text}},
       {'updateTextStyle':{'range':rg,'textStyle':{'weightedFontFamily':{'fontFamily':'Arial'},'fontSize':{'magnitude':11,'unit':'PT'}},'fields':'weightedFontFamily,fontSize'}},
       {'updateParagraphStyle':{'range':rg,'paragraphStyle':{'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'}},'fields':'spaceAbove,spaceBelow'}},
       {'updateParagraphStyle':{'range':{'tabId':tab,'startIndex':1,'endIndex':1+u(text.split('\n')[0])},'paragraphStyle':{'namedStyleType':'HEADING_1','keepWithNext':True},'fields':'namedStyleType,keepWithNext'}},
       {'updateTextStyle':{'range':{'tabId':tab,'startIndex':1,'endIndex':1+u(text.split('\n')[0])},'textStyle':{'fontSize':{'magnitude':18,'unit':'PT'},'bold':True},'fields':'fontSize,bold'}}]
  link='Source and reproduction evidence';start=1+u(text[:text.index(link)])
  req.append({'updateTextStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+u(link)},'textStyle':{'link':{'url':'https://github.com/alejoacelas/2026-09-workspace-tools-comparison/blob/'+COMMIT+'/hunt/confirmed.json'},'underline':True},'fields':'link,underline'}})
  # Native image at its reserved paragraph, after all text-style ranges were applied.
  req.append({'insertInlineImage':{'location':{'tabId':tab,'index':1+u(top)},'uri':BASE+c['id']+'.png','objectSize':{'width':{'magnitude':468,'unit':'PT'}}}})
  b.update(id,req)
  after=b.state(id);t=next(t for t in after['tabs'] if t['tabProperties']['tabId']==tab)
  assert t['documentTab'].get('inlineObjects'),c['id']
  collection['cases'][c['id']]=tab;b.save('collection.json',collection)
  print('Published',c['short'],flush=True)
 # Page margins and guide naming only; no case body rewrite.
 b.update(id,[{'updateDocumentTabProperties':{'tabProperties':{'tabId':collection['guide_tab'],'title':'Guide'},'fields':'title'}},{'updateDocumentStyle':{'documentStyle':{'marginTop':{'magnitude':36,'unit':'PT'},'marginBottom':{'magnitude':36,'unit':'PT'},'marginLeft':{'magnitude':54,'unit':'PT'},'marginRight':{'magnitude':54,'unit':'PT'}},'fields':'marginTop,marginBottom,marginLeft,marginRight'}}])
 print('https://docs.google.com/document/d/'+id+'/edit')
if __name__=='__main__':main()
