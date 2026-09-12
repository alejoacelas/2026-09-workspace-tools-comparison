"""Personal synthetic navigation and public-URL image checks; no deletes/shares.
Run repos/gdoc/.venv/bin/python hunt/round2/navigation.py.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'hunt'))
import live as b
OUT=ROOT/'hunt/round2';rows=[]
URL='https://raw.githubusercontent.com/alejoacelas/2026-09-workspace-tools-comparison/main/figures/gdoc-bold-loss.png'
URL2='https://raw.githubusercontent.com/alejoacelas/2026-09-workspace-tools-comparison/main/figures/shared-nested-list.png'

def tabs(items,depth=0):
 for t in items:
  yield t,depth
  yield from tabs(t.get('childTabs',[]),depth+1)

def alltext(x):
 if isinstance(x,dict):
  if 'textRun' in x:return x['textRun'].get('content','')
  return ''.join(alltext(v) for v in x.values())
 if isinstance(x,list):return ''.join(alltext(v) for v in x)
 return ''

def record(name,ok,details):
 rows.append({'case':name,'pass':ok,'details':details})
 (OUT/'navigation.json').write_text(json.dumps({'pin':'dbfa4c34bfa699ee8dd9839da85eea1fac177d44','cases':rows},indent=2)+'\n')
 print(name,'PASS' if ok else 'DIFFERENCE',flush=True)

def run(args):
 r=b.cli(args)
 b.save('r2-navigation-last-cli.json',r)
 if r['returncode']!=0:print('CLI nonzero',args[0],r['returncode'],flush=True)
 return r

def images_native(doc):
 return {obj:{'tab':t['tabProperties']['title'],'size':data['inlineObjectProperties']['embeddedObject'].get('size',{})} for t,_ in tabs(doc['tabs']) for obj,data in t.get('documentTab',{}).get('inlineObjects',{}).items()}

id=b.new('Synthetic r2 navigation and image controls');doc=b.state(id);main=doc['tabs'][0]['tabProperties']['tabId'];b.save('r2-navigation-ledger.json',{'id':id})
b.update(id,[{'updateDocumentTabProperties':{'tabProperties':{'tabId':main,'title':'Main'},'fields':'title'}}])
ids={'Main':main}
for name,parent,index in [('Branch','Main',0),('Leaf','Branch',0),('Peer',None,1)]:
 props={'title':name,'index':index}
 if parent:props['parentTabId']=ids[parent]
 result=b.update(id,[{'addDocumentTab':{'tabProperties':props}}]);ids[name]=result['replies'][0]['addDocumentTab']['tabProperties']['tabId']
b.save('r2-navigation-ledger.json',{'id':id,'tabs':ids})
content={'Main':[('Repeated','HEADING_1'),('Repeated','HEADING_2'),('Detail','HEADING_3'),('Deep','HEADING_6'),('Styled title','TITLE'),('Root marker','NORMAL_TEXT')],'Branch':[('Branch heading','HEADING_2'),('Branch marker','NORMAL_TEXT')],'Leaf':[('Leaf heading','HEADING_3'),('Leaf marker','NORMAL_TEXT')],'Peer':[('Peer heading','HEADING_1'),('Peer marker','NORMAL_TEXT')]}
for name,paras in content.items():
 text='\n'.join(p[0] for p in paras)+'\n';req=[{'insertText':{'location':{'index':1,'tabId':ids[name]},'text':text}}];pos=1
 for text,style in paras:
  end=pos+len((text+'\n').encode('utf-16-le'))//2
  req.append({'updateParagraphStyle':{'range':{'startIndex':pos,'endIndex':end,'tabId':ids[name]},'paragraphStyle':{'namedStyleType':style},'fields':'namedStyleType'}});pos=end
 b.update(id,req)
doc=b.state(id);b.save('r2-navigation-native-before.json',doc)
native=[{'title':t['tabProperties']['title'],'depth':d} for t,d in tabs(doc['tabs'])]
r=run(['tabs',id,'--json']);got=json.loads(r['stdout']).get('tabs',[]);actual=[{'title':t['title'],'depth':t['nesting_level']} for t in got]
record('tab_tree_depth',actual==native,{'expected':native,'actual':actual})
r=run(['cat',id,'--all-tabs']);record('all_tab_markers',all(name+' marker' in r['stdout'] for name in ['Root','Branch','Leaf','Peer']),{'all_four_markers_present':all(name+' marker' in r['stdout'] for name in ['Root','Branch','Leaf','Peer'])})
r=run(['cat',id,'--tab','Leaf']);record('grandchild_read_by_title','Leaf marker' in r['stdout'] and 'Root marker' not in r['stdout'],{'returned_text':r['stdout']})
r=run(['structure',id]);raw=json.loads(r['stdout']);record('structure_full_topology',[t['tabProperties']['title'] for t,_ in tabs(raw.get('tabs',[]))]==[t['title'] for t in native],{'tab_titles':[t['tabProperties']['title'] for t,_ in tabs(raw.get('tabs',[]))]})
r=run(['structure',id,'--tab','Branch']);raw=json.loads(r['stdout']);sub=raw.get('tab',{});record('structure_selected_subtree',sub.get('tabProperties',{}).get('title')=='Branch' and [t['tabProperties']['title'] for t in sub.get('childTabs',[])]==['Leaf'],{'selected_title':sub.get('tabProperties',{}).get('title'),'children':[t['tabProperties']['title'] for t in sub.get('childTabs',[])]})
r=run(['structure',id,'--fields','revisionId,tabs(tabProperties)']);raw=json.loads(r['stdout']);record('structure_supported_mask',r['returncode']==0 and 'revisionId' in raw and 'tabs' in raw,{'keys':list(raw)})
headings=[]
for e in doc['tabs'][0]['documentTab']['body']['content']:
 p=e.get('paragraph',{});s=p.get('paragraphStyle',{})
 if s.get('namedStyleType','').startswith('HEADING_'):headings.append({'text':alltext(p).strip(),'level':int(s['namedStyleType'][-1]),'heading_id':s['headingId']})
r=run(['toc',id,'--tab','Main','--json']);got=json.loads(r['stdout'])['headings'];observed=[{k:h[k] for k in ['text','level','heading_id']} for h in got]
record('toc_repeated_titles_and_levels',observed==headings,{'expected_titles_levels':[(h['text'],h['level']) for h in headings],'actual_titles_levels':[(h['text'],h['level']) for h in got],'distinct_ids_for_repeated_titles':got[0]['heading_id']!=got[1]['heading_id']})
record('toc_deep_links',all('?tab='+main in h['link'] and h['link'].endswith('#heading='+h['heading_id']) for h in got),{'all_links_have_selected_tab_and_exact_heading_id':all('?tab='+main in h['link'] and h['link'].endswith('#heading='+h['heading_id']) for h in got)})
r=run(['toc',id,'--tab','Main','--max-depth','2','--json']);got=json.loads(r['stdout'])['headings'];record('toc_depth_filter',[(h['text'],h['level']) for h in got]==[('Repeated',1),('Repeated',2)],{'actual':[(h['text'],h['level']) for h in got]})
r=run(['toc',id,'--tab','Leaf','--no-links']);record('toc_grandchild_no_links','Leaf heading' in r['stdout'] and 'https://' not in r['stdout'],{'text':r['stdout']})

# Only already-public synthetic report PNG URLs; CLI never uploads/deletes a temp file.
r=run(['insert-image',id,URL,'--tab','Main','--end','--width','112','--height','64']);doc=b.state(id);a=images_native(doc)
record('image_insert_explicit_dimensions',r['returncode']==0 and len(a)==1 and next(iter(a.values()))['size']['width']['magnitude']==112 and abs(next(iter(a.values()))['size']['height']['magnitude']-49.6)<0.001,{'returncode':r['returncode'],'native_images':list(a.values()),'requested_bounding_box_pt':[112,64],'source_png_px':[1120,496],'expected_fitted_size_pt':[112,49.6]})
r=run(['insert-image',id,URL,'--tab','Leaf','--end','--width','140']);doc=b.state(id);a=images_native(doc)
record('image_insert_grandchild_width_only',r['returncode']==0 and len(a)==2 and any(x['tab']=='Leaf' and x['size']['width']['magnitude']==140 for x in a.values()),{'returncode':r['returncode'],'native_images':list(a.values())})
r=run(['images',id,'--json']);got=json.loads(r['stdout']).get('images',[]);b.save('r2-navigation-image-inventory.json',got)
record('image_inventory_all_nested_tabs',set(x['id'] for x in got)==set(a),{'native_count':len(a),'reported_count':len(got),'reported_sizes':[{'type':x['type'],'width':x['width_pt'],'height':x['height_pt']} for x in got]})
obj=next(k for k,v in a.items() if v['tab']=='Leaf');old=a[obj];r=run(['replace-image',id,obj,URL2]);newdoc=b.state(id);new=images_native(newdoc);b.save('r2-navigation-native-after.json',newdoc)
record('image_replace_preserves_identity_size_tab',r['returncode']==0 and obj in new and new[obj]==old,{'returncode':r['returncode'],'before':old,'after':new.get(obj),'same_object_id':obj in new})
r=run(['images',id,obj,'--json']);got=json.loads(r['stdout']).get('images',[]);record('image_inventory_select_one',len(got)==1 and got[0]['id']==obj,{'returned_count':len(got),'correct_id':len(got)==1 and got[0]['id']==obj})
(OUT/'navigation.md').write_text('# Native navigation and public-URL image controls\n\n'+str(len(rows))+' checks on one synthetic personal Doc with Main → Branch → Leaf nesting and a Peer tab.\n\n| Check | Result |\n|---|---|\n'+'\n'.join('| '+r['case']+' | '+('pass' if r['pass'] else 'difference')+' |' for r in rows)+'\n\nRaw resource identifiers and signed image URLs are confined to ignored local scratch. Public evidence publishes only synthetic headings, tab names, dimensions, counts and boolean comparisons. Images were inserted/replaced using already-public synthetic report PNG URLs; no local-image upload, sharing, temporary deletion or collection mutation occurred.\n\nThese are bounded positive controls, not proof all heading or image scenarios work. Replacement checks establish retained object identity/size/tab, not pixel-level center-crop fidelity.\n')

# Source aspect ratio is part of the oracle: objectSize is a fitting box.
with (OUT/"navigation.md").open("a") as f:
 f.write("\nImage insertion preserved aspect ratio: a 1120×496 PNG requested within 112×64pt became 112×49.6pt; width-only 140pt became 140×62pt. Google documents aspect-preserving fitting in its [objectSize rules](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request#InsertInlineImageRequest).\n")
