"""Offline boundary hypotheses for one phantom-match family; no Google calls."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'repos/gdoc'))
from gdoc.api.docs import find_text_in_document
CASES=[('person',{'person':{'personProperties':{'email':'person@example.invalid'}}}),('date',{'dateElement':{'dateElementProperties':{'displayText':'2030-01-02'}}}),('file',{'richLink':{'richLinkProperties':{'title':'Budget','uri':'https://example.invalid/budget'}}}),('footnote',{'footnoteReference':{'footnoteId':'synthetic-footnote','footnoteNumber':'1'}}),('image',{'inlineObjectElement':{'inlineObjectId':'synthetic-image'}}),('horizontal_rule',{'horizontalRule':{}}),('page_break',{'pageBreak':{}}),('column_break',{'columnBreak':{}})]
def run(name,elements,expected):
 body={'content':[{'startIndex':1,'endIndex':elements[-1]['endIndex'],'paragraph':{'elements':elements}}]}
 matches=find_text_in_document(None,'Before  after',match_case=True,body=body)
 return {'case':name,'expectation':expected,'matches':matches,'body':body}
rows=[]
for name,element in CASES:
 elements=[{'startIndex':1,'endIndex':8,'textRun':{'content':'Before '}},{'startIndex':8,'endIndex':9,**element},{'startIndex':9,'endIndex':16,'textRun':{'content':' after\n'}}]
 rows.append(run(name,elements,'Hypothesis: a nontext boundary should not synthesize adjacent literal text; native person oracle independently confirms this.'))
 assert rows[-1]['matches']==[{'startIndex':1,'endIndex':15}]
for name,text,expected in [('actual_double_space','Before  after\n',True),('single_space','Before after\n',False),('line_break','Before\n after\n',False),('literal_object_replacement','Before \ufffc after\n',False)]:
 r=run(name,[{'startIndex':1,'endIndex':len(text)+1,'textRun':{'content':text}}],'match' if expected else 'no match');assert bool(r['matches'])==expected;rows.append(r)
(ROOT/'hunt/round2/chips-matching-results.json').write_text(json.dumps({'scope':'12 offline matching cases; 8 nontext variants of one mechanism, 4 ordinary text controls. Only person/file variants are live-validated elsewhere.','cases':rows},indent=2)+'\n')
print('8 nontext variants cross boundary; 4 ordinary text controls match expectations')
