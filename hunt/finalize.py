"""Finish guide, correct the reviewed H07 image, and verify/export collection."""
import json,sys
import live as b
commit=sys.argv[1]
c=json.loads((b.LOCAL/'collection.json').read_text());id=c['id'];d=b.state(id)
tab=c['cases']['h07-nested-emphasis'];t=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)
obj=next(iter(t['documentTab']['inlineObjects']))
b.update(id,[{'replaceImage':{'imageObjectId':obj,'tabId':tab,'uri':'https://raw.githubusercontent.com/alejoacelas/2026-09-workspace-tools-comparison/'+commit+'/hunt/figures/h07-nested-emphasis.png'}}])
guide='gdoc bug hunt — confirmed cases\n9 live-confirmed examples from a parallel investigation\n\nThree agents tested 68 offline specimens covering table and block parsing, inline Markdown, and native document export. Selected candidates were then exercised through the pinned gdoc CLI against synthetic Google Docs and checked independently. These deliberately difficult specimens do not estimate a real-world error rate.\n\nThe nine case tabs include eight examples beyond the previous comparison and a live confirmation of its escaped-pipe finding. They overlap broader existing campaign repair areas; nine examples does not mean nine unrelated or previously unknown bug families.\n\nHow to read the cases\nEvery tab has a reconstructed Pillow Before / Expected / Observed illustration, followed by Bug, Commands, setup, and evidence. The pictures are not screenshots. H01–H07 show successful writes with incorrect native content or styling. H08–H09 show successful selected-tab reads that omit content or numbering; the source documents remain unchanged.\n\nScope\nTarget: public gdoc v0.21.0, commit dbfa4c34. H01–H07 use write --tab, the native Markdown writer. Whole-document Drive import uses a different converter. For H08–H09, plain cat is a passing control for the specific content lost by cat --tab; it is not a guarantee of complete formatting fidelity. No upstream fix was made in this hunt.\n\nGround truth\nExpected Markdown meaning follows explicit synthetic expectations checked against CommonMark/GFM, with an independent parser as a cross-check. Google Docs native readback verifies the writes. The extra read cases were also checked against a rendered Google PDF. Workspace agreement is supplementary: it shares the reference Markdown parser and is not an independent vote.\n\nFollow-up candidates\nAdditional offline observations—including smart-chip label omission and ordered-list counter variants—remain in the evidence, outside these live-confirmed tabs. Malformed input and unsupported shapes are labeled separately.\n\nEvidence and runnable reproducers\n'
guide=guide.replace('\n\n','\n')
tab=c['guide_tab'];d=b.state(id);body=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)['documentTab']['body']['content'];end=body[-1]['endIndex']-1
u=lambda s:len(s.encode('utf-16-le'))//2
req=[]
if end>1:req.append({'deleteContentRange':{'range':{'tabId':tab,'startIndex':1,'endIndex':end}}})
req.append({'insertText':{'location':{'tabId':tab,'index':1},'text':guide}})
rg={'tabId':tab,'startIndex':1,'endIndex':1+u(guide)}
req.extend([{'updateTextStyle':{'range':rg,'textStyle':{'weightedFontFamily':{'fontFamily':'Arial'},'fontSize':{'magnitude':11,'unit':'PT'}},'fields':'weightedFontFamily,fontSize'}},{'updateParagraphStyle':{'range':rg,'paragraphStyle':{'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':5,'unit':'PT'}},'fields':'spaceAbove,spaceBelow'}}])
for title,style in [('gdoc bug hunt — confirmed cases','TITLE'),('How to read the cases','HEADING_2'),('Scope','HEADING_2'),('Ground truth','HEADING_2'),('Follow-up candidates','HEADING_2')]:
 start=1+u(guide[:guide.index(title)]);req.append({'updateParagraphStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+u(title)},'paragraphStyle':{'namedStyleType':style,'keepWithNext':True},'fields':'namedStyleType,keepWithNext'}})
label='Evidence and runnable reproducers';start=1+u(guide[:guide.index(label)])
req.append({'updateTextStyle':{'range':{'tabId':tab,'startIndex':start,'endIndex':start+u(label)},'textStyle':{'link':{'url':'https://github.com/alejoacelas/2026-09-workspace-tools-comparison/tree/main/hunt'}},'fields':'link'}})
b.update(id,req)
# Apply page geometry to every document tab; tab-specific defaults can differ.
layout=[]
for t in b.state(id)['tabs']:
 layout.append({'updateDocumentStyle':{'tabId':t['tabProperties']['tabId'],'documentStyle':{'marginTop':{'magnitude':36,'unit':'PT'},'marginBottom':{'magnitude':36,'unit':'PT'},'marginLeft':{'magnitude':54,'unit':'PT'},'marginRight':{'magnitude':54,'unit':'PT'}},'fields':'marginTop,marginBottom,marginLeft,marginRight'}})
for old,new in [('steps7 and8','steps 7 and 8'),('Steps7 and8','Steps 7 and 8'),('displays7 and8','displays 7 and 8')]:
 layout.append({'replaceAllText':{'containsText':{'text':old,'matchCase':True},'replaceText':new,'tabsCriteria':{'tabIds':[c['cases']['h09-numbered-list-read']]}}})
b.update(id,layout)
d=b.state(id);b.save('collection-native.json',d)
assert len(d['tabs'])==10
checks=[]
for key,tab in c['cases'].items():
 t=next(t for t in d['tabs'] if t['tabProperties']['tabId']==tab)['documentTab'];assert len(t['inlineObjects'])==1
 from confirm import text
 words=text(t['body']);assert words.index('Bug.')<words.index('Commands')<words.index('Evidence:')
 checks.append({'case':key,'images':len(t['inlineObjects']),'description_command_order':True})
(b.ROOT/'hunt/publication-checks.json').write_text(json.dumps({'tabs':len(d['tabs']),'cases':checks,'pdf_visual_qa':'pending'},indent=2)+'\n')
r=b.cli(['export',id,'--out',str(b.LOCAL/'collection.pdf')]);assert r['returncode']==0,r
print('Verified10tabs/9images; exported collection.pdf',flush=True)
