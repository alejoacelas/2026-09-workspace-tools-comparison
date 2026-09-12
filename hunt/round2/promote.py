"""Curate independently confirmed live examples; preserve exact evidence triggers."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
out=[]
def read(name):return json.loads((R/name).read_text())
def seg(text,**kw):return {'text':text,**kw}
def state(data,kind='segments',**kw):return {'kind':kind,'data':data,**kw}
def case(n,slug,title,intent,bug,**kw):
 c={'id':f'h{n:02d}-'+slug,'short':f'H{n:02d}','title':title,'intent':intent,'bug':bug,'markdown':'','status':'Live confirmed; command returned success','novelty':'Additional concrete regression trigger; broad campaign repair areas can overlap.','source':'https://github.com/LucaDeLeo/gdoc/tree/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc',**kw};out.append(c);return c
chips=read('chips-results.json');selected=next(x for x in chips['reads'] if x['route']=='selected_tab')
assert selected['returncode']==0 and 'Person:  owns budget.' in selected['stdout']
assert any('person' in x['native_types'] for x in chips['native'])
case(10,'chip-read','Selected-tab read omits smart chips','Read the owner named in a native person chip.',
 'The selected-tab reader skips person, date and file chips, removing their visible names, dates and titles. Ordinary adjacent text and links survive. Plain gdoc cat and Workspace retain these chips. The illustrated name is anonymized.',
 before=state([[seg('Person: '),seg('Alex Example',chip=True),seg(' owns budget.')]],label='BEFORE — NATIVE PERSON CHIP',diagnostic='Name anonymized: Alex Example represents the account owner.'),
 expected=state('Person: Alex Example owns budget.','source',label='EXPECTED — READABLE CONTENT',diagnostic='Retain the visible name; a hyperlink is also acceptable.'),
 observed=state('Person:  owns budget.','source',label='OBSERVED — SELECTED-TAB OUTPUT'),
 commands='gdoc cat DOC --tab TAB --account PERSONAL\ngdoc cat DOC --account PERSONAL',
 setup='Setup: create native chips with chips.py. Alex Example represents the account owner; no other person was contacted.')
sheets=read('sheets-results.json')['cases'];r=next(x for x in sheets if x['id']=='tsv-crlf')
assert r['returncode']==0 and r['actual']==[['Item','Value\r'],['Budget','100\r']]
case(11,'tsv-crlf','Windows TSV imports hidden carriage returns','Import a two-column TSV file whose lines end with CRLF.',
 'The TSV reader removes LF but leaves CR in each final cell. The cells can look normal, but exact comparisons and header lookup fail. The same values with LF-only TSV or CRLF CSV import correctly.',
 before=state(r'Item\tValue\r\n'+'\n'+r'Budget\t100\r\n','source',label='BEFORE — TSV BYTES (ESCAPED)'),
 expected=state([['Item','Value'],['Budget','100']],'sheet',label='EXPECTED — GOOGLE SHEETS',diagnostic='Stored B2: "100". Exact comparison with "100": TRUE.'),
 observed=state([['Item','Value'],['Budget','100']],'sheet',label='OBSERVED — GOOGLE SHEETS',diagnostic=r'Stored B2: "100\r". Exact comparison: FALSE. The CR is invisible.'),
 commands='gdoc cells SHEET Data!A1 --file crlf.tsv --account PERSONAL',setup='Setup: use literal CRLF line endings, not the displayed backslash escapes. The diagram normalizes the tested range to A1:B2.')
links=read('links-results.json')['live']
r=next(x for x in links if x['id']=='ten-digit-account');assert r['returncode']==0 and r['after']['text']=='Revenue account\n'
# The independent Google PDF extraction confirms the observed marker is1.
assert '1.' in r['pdf_text'] and 'Revenue account' in r['pdf_text']
case(12,'long-number','Ten-digit identifier becomes list numbering','Write the literal line identifying revenue account 1234567890.',
 'A line starting with a ten-digit number and a period is treated as a numbered list. The identifier disappears and Google renders item 1 instead. CommonMark limits ordered-list markers to nine digits; the independent parser treats this input as plain text.',
 markdown=r['markdown'],expected=state([[seg(r['markdown'])]]),observed=state([[seg('1.  Revenue account')]]),commands='gdoc cat DOC --tab TAB --account PERSONAL\ngdoc write DOC specimen.md --tab TAB --account PERSONAL')
r=next(x for x in links if x['id']=='bracket-link-label');assert r['returncode']==0 and not r['actual']['links']
case(13,'bracket-link','Bracketed link label becomes literal Markdown','Create a Finance [Q3] hyperlink.',
 'A valid link label containing nested square brackets is not parsed as a link. The entire Markdown expression becomes visible prose. gdoc also emits this syntax when exporting a native link with that label, so its own output cannot make the round trip.',
 markdown=r['markdown'],expected=state([[seg('Read '),seg('Finance [Q3]',link=True),seg('.')]]),observed=state([[seg(r['actual']['text'])]],label='OBSERVED — STORED DOCUMENT TEXT'),commands='gdoc cat DOC --tab TAB --account PERSONAL\ngdoc write DOC specimen.md --tab TAB --account PERSONAL')
r=next(x for x in links if x['id']=='entity-query-link');assert r['returncode']==0 and r['actual']['links']==['https://example.com/report?a=1&amp;b=2']
case(14,'entity-url','Entity text changes hyperlink parameters','Create a Budget link whose query has parameters a=1 and b=2.',
 'The Markdown entity &amp; is stored literally in the link destination. Its second query key becomes amp;b rather than b. The visible Budget label remains correct, so checking only document text misses the failure.',
 markdown=r['markdown'],expected=state([[seg('Open '),seg('Budget',link=True),seg('.')]],diagnostic='URL: https://example.com/report?a=1&b=2'),observed=state([[seg('Open '),seg('Budget',link=True),seg('.')]],diagnostic='URL: https://example.com/report?a=1&amp;b=2'),commands='gdoc cat DOC --tab TAB --account PERSONAL\ngdoc write DOC specimen.md --tab TAB --account PERSONAL')
r=next(x for x in read('structure-results.json')['cases'] if x['id']=='colspan_label_control')
assert r['edit']['returncode']==0 and 'Merged AUpdated' in r['after']['text'] and r['after']['tables'][0]['cells'][0][2]['text']=='C'
merged=lambda a,b:state([{'text':a,'span':2},{'text':b,'span':1}],'merged-row')
case(15,'merged-label','Merged label receives its neighbor’s edit','Replace the visible cell immediately right of Merged A with Updated.',
 'Label-based cell selection moves one underlying column instead of past the merged span. It targets a covered slot; Google appends the replacement into the merged label, leaving the visible neighbor unchanged. Explicit column selection succeeds. A fresh three-column-span specimen reproduced the error.',
 before={**merged('Merged A','C'),'label':'BEFORE — LABEL SPANS TWO COLUMNS'},expected=merged('Merged A','Updated'),observed=merged('Merged AUpdated','C'),commands='gdoc edit DOC Updated --cell "Merged A" --tab TAB --account PERSONAL',setup='Setup: import the one-row colspan=2 table from structure.py. The CLI documents --cell as replacing the cell to the right of the label; --col 2 is the passing control.')
r=next(x for x in read('chips-edits-results.json') if x['case']=='person_cross_gap');oracle=read('chips-oracle-results.json')
assert r['returncode']==0 and r['before']['person_count']==1 and r['after']['person_count']==0 and oracle['occurrences_changed']==0 and oracle['person_count_after']==1
scene=state([[seg('Before '),seg('Alex Example',chip=True),seg(' after.')]])
case(16,'chip-phantom-match','A phantom text match deletes the chip','Replace the literal phrase "Before  after" with "Replacement".',
 'gdoc concatenates text on either side of a chip into a phrase that is not actually contiguous, then deletes the chip while replacing that phrase. Both person and file chips were lost. Google’s native replacement and Workspace find zero matches and preserve the chip. Adjacent ordinary edits pass.',
 before={**scene,'label':'BEFORE — NATIVE PERSON CHIP','diagnostic':'Name anonymized. Selected-tab cat misleadingly reports: Before  after.'},expected={**scene,'diagnostic':'Native Google and Workspace: 0 matches; chip preserved.'},observed=state([[seg('Replacement.')]],diagnostic='gdoc reports 1 replacement; native person count drops from 1 to 0.'),commands='gdoc cat DOC --tab TAB --account PERSONAL\ngdoc edit DOC "Before  after" Replacement --tab TAB --account PERSONAL',setup='Setup: use the person-chip paragraph from chips-edits.py; two spaces separate Before and after in the search phrase. Alex Example is an anonymized account name.')
(R/'confirmed.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print('Promoted',len(out),'round2 cases')
