"""Promote live success-with-wrong-content cases; expected values are independent."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
META={
'h01-escaped-pipe':('H01','Escaped pipe discards the value','Create a two-column table whose key is A|B and whose value is 100.','A backslash-escaped pipe is split as a column boundary. The resulting table loses 100.','Known comparison case; now also live-confirmed.','table', [['Key','Value'],['A|B','100']]),
'h02-empty-edge-cell':('H02','Empty cell shifts the value','Create a table with an empty Key cell and 100 under Value.','A compact empty first cell is stripped before splitting the row. 100 moves into Key, leaving Value blank. Adding a space inside the empty cell avoids this particular trigger.','Additional trigger within the broad Markdown grammar area.','table',[['Key','Value'],['','100']]),
'h03-fence-close':('H03','Code fence ends too early','Write the whole fenced specimen as literal code.','A fence-like line with trailing text is mistaken for the closing fence. That line disappears and the following literal asterisks become bold formatting.','Additional fence-grammar regression.','code','alpha\n```not-a-close\n**literal**'),
'h04-link-title':('H04','Link title enters the destination','Create a Policy hyperlink to https://example.com/policy.','The optional Markdown title is included in the actual hyperlink URL. The visible label looks correct, so a text-only check misses the failure.','Additional trigger within the existing link grammar area.','link','Read Policy.'),
'h05-code-delimiter':('H05','Double-backtick code is corrupted','Write a code span containing one literal backtick.','The parser treats a multi-backtick delimiter as single-backtick fragments. It changes the literal code and leaves delimiter characters in the visible sentence.','Additional code-span regression trigger.','segments',[[{'text':'Use '},{'text':'a`b','code':True},{'text':' now.'}]]),
'h06-code-backslash':('H06','Trailing backslash breaks code','Write the literal code C:\\temp\\, including its final backslash.','Backslash escaping is applied before code-span recognition. The closing delimiter is treated as escaped: code formatting disappears and the path changes.','Additional code-span regression trigger.','segments',[[{'text':'Use '},{'text':'C:\\temp\\','code':True},{'text':' now.'}]]),
'h07-nested-emphasis':('H07','Literal code breaks surrounding bold','Make the whole sentence bold while preserving a**b as literal code.','Asterisks inside the code span terminate the surrounding emphasis. The code text is altered and formatting markers leak into the output.','Additional code-span precedence trigger; same broad repair area as H05–H06.','segments',[[{'text':'Use ','bold':True},{'text':'a**b','bold':True,'code':True},{'text':' today','bold':True}]]),
}
def segments(body):
 lines=[]
 for el in body:
  if 'paragraph' not in el:continue
  line=[]
  for e in el['paragraph']['elements']:
   r=e.get('textRun',{});style=r.get('textStyle',{});parts=r.get('content','').split('\n')
   for n,t in enumerate(parts):
    if t:line.append({'text':t,'bold':style.get('bold',False),'code':style.get('weightedFontFamily',{}).get('fontFamily')=='Courier New','link':bool(style.get('link'))})
    if n<len(parts)-1:
     if line:lines.append(line)
     line=[]
  if line:lines.append(line)
 return lines
out=[]
for r in json.loads((ROOT/'live-results.json').read_text()):
 if r['returncode']!=0:continue
 key=r['id'];short,title,intent,bug,novelty,kind,expected=META[key]
 c={'id':key,'short':short,'title':title,'intent':intent,'bug':bug,'novelty':novelty,'markdown':r['markdown'],'status':'Live Google Docs failure; gdoc reports success','source':'https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py','commands':'gdoc cat DOC --tab TAB --account PERSONAL\ngdoc write DOC specimen.md --tab TAB --account PERSONAL'}
 if kind=='table':
  observed=r['state']['tables'][0];assert observed!=expected
  c['expected']={'kind':'table','data':expected};c['observed']={'kind':'table','data':observed}
 else:
  actual=segments(r['state']['body'])
  if kind=='code':exp=[[{'text':t,'code':True}] for t in expected.splitlines()]
  elif kind=='link':exp=[[{'text':'Read '},{'text':'Policy','link':True},{'text':'.'}]]
  else:exp=expected
  c['expected']={'kind':'segments','data':exp};c['observed']={'kind':'segments','data':actual}
  if kind=='link':
   urls=[e['textRun']['textStyle']['link']['url'] for el in r['state']['body'] if 'paragraph' in el for e in el['paragraph']['elements'] if e.get('textRun',{}).get('textStyle',{}).get('link')]
   assert urls==['https://example.com/policy "Policy handbook"']
   c['expected']['diagnostic']='Link target: https://example.com/policy';c['observed']['diagnostic']='Link target: '+urls[0]
  else:
   actual_text='\n'.join(''.join(s['text'] for s in line) for line in actual)
   expected_text='\n'.join(''.join(s['text'] for s in line) for line in exp)
   assert actual_text!=expected_text,(key,actual_text)
 out.append(c)
extra=json.loads((ROOT/'export-extra-results.json').read_text()) if (ROOT/'export-extra-results.json').exists() else None
if extra and extra['native_nested_table_confirmed']:
 read=next(r for r in extra['reads'] if r['route']=='selected_tab')
 assert read['returncode']==0 and not read['contains_inner_materials'] and not read['contains_inner_475']
 assert 'Materials' in extra['native_text'] and '475' in extra['native_text']
 out.append({'id':'h08-nested-table-read','short':'H08','title':'Selected-tab read drops nested table contents',
 'intent':'Read the selected tab, retaining the contents of its nested table.',
 'bug':'The selected-tab reader omits the inner table entirely. Materials and 475 disappear without an error. Reading the same document without --tab retains both values; the source document itself is unchanged.',
 'novelty':'Additional native read-path content omission; independently confirmed on a real nested table.',
 'markdown':'','status':'Live selected-tab read failure; gdoc returns success',
 'before':{'label':'BEFORE — NATIVE GOOGLE DOC EXCERPT','kind':'nested-table','data':[]},
 'expected':{'label':'EXPECTED — READABLE CONTENT','kind':'source','data':'Outer cell\nMaterials  475','diagnostic':'Any text representation retaining both inner values is acceptable.'},
 'observed':{'label':'OBSERVED — SELECTED-TAB OUTPUT EXCERPT','kind':'source','data':'Outer cell','diagnostic':'Both inner values are absent from the complete command output.'},
 'commands':'gdoc cat DOC --tab TAB --account PERSONAL\ngdoc cat DOC --account PERSONAL',
 'setup':'Setup: import the synthetic nested-table HTML from export-extra-probe.py; the first command fails the content check, the second is the passing control.',
 'source':'https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py'})
# The rendered native PDF and default-cat control independently retain7/8.
if extra and (ROOT.parent/'.local-hunt/export-extra-pdf.txt').exists():
 pdf=(ROOT.parent/'.local-hunt/export-extra-pdf.txt').read_text()
 assert '7.' in pdf and 'Review budget' in pdf and '8.' in pdf and 'Approve purchase' in pdf
 read=next(r for r in extra['reads'] if r['route']=='selected_tab')
 assert '- Review budget' in read['stdout'] and '- Approve purchase' in read['stdout']
 out.append({'id':'h09-numbered-list-read','short':'H09','title':'Selected-tab read changes numbers to bullets',
 'intent':'Read a procedure while retaining steps7 and8.',
 'bug':'The selected-tab reader emits unordered bullet markers for an imported numbered list. Steps7 and8 disappear. The native Google PDF displays7 and8, and gdoc cat without --tab preserves those numbers. The source document is unchanged.',
 'novelty':'Additional live list-read trigger; distinct from the offline counter examples.',
 'markdown':'','status':'Live selected-tab read failure; gdoc returns success',
 'before':{'label':'BEFORE — NATIVE GOOGLE DOC EXCERPT','kind':'segments','data':[[{'text':'7.  Review budget'}],[{'text':'8.  Approve purchase'}]]},
 'expected':{'label':'EXPECTED — READABLE NUMBERED STEPS','kind':'source','data':'7. Review budget\n8. Approve purchase'},
 'observed':{'label':'OBSERVED — SELECTED-TAB OUTPUT EXCERPT','kind':'source','data':'- Review budget\n- Approve purchase'},
 'commands':'gdoc cat DOC --tab TAB --account PERSONAL\ngdoc cat DOC --account PERSONAL',
 'setup':'Setup: import the HTML ol start=7 specimen from export-extra-probe.py. Google PDF confirms the numbering; the second command is the passing read control.',
 'source':'https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py'})
(ROOT/'confirmed.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('Promoted',len(out),'live cases')
