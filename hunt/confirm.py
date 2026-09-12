"""Independent live check of selected agent candidates through pinned gdoc CLI."""
import json
import live as b
CASES=[
 ('h01-escaped-pipe','| Key | Value |\n| --- | --- |\n| A\\|B | 100 |'),
 ('h02-empty-edge-cell','| Key | Value |\n| --- | --- |\n||100|'),
 ('h03-fence-close','```\nalpha\n```not-a-close\n**literal**\n```'),
 ('h04-link-title','Read [Policy](https://example.com/policy "Policy handbook").'),
 ('h05-code-delimiter','Use ``a`b`` now.'),
 ('h06-code-backslash',r'Use `C:\temp\` now.'),
 ('h07-nested-emphasis','**Use `a**b` today**'),
]
def text(x):
 if isinstance(x,dict):
  if 'textRun' in x:return x['textRun'].get('content','')
  return ''.join(text(v) for v in x.values())
 if isinstance(x,list):return ''.join(text(v) for v in x)
 return ''
def summarize(d):
 body=d['tabs'][0]['documentTab']['body']['content']
 return {'text':text(body),'body':body,'tables':[[[text(c['content']).rstrip('\n') for c in r['tableCells']] for r in el['table']['tableRows']] for el in body if 'table' in el]}
def main():
 ledger=json.loads((b.LOCAL/'fixtures.json').read_text()) if (b.LOCAL/'fixtures.json').exists() else {}
 out=[]
 for key,md in CASES:
  id=ledger.get(key)
  if not id:
   id=b.new('Synthetic gdoc hunt — '+key);ledger[key]=id;b.save('fixtures.json',ledger)
  d=b.state(id);tab=d['tabs'][0]['tabProperties']['tabId'];f=b.LOCAL/(key+'.md');f.write_text(md)
  read=b.cli(['cat',id,'--tab',tab]);assert read['returncode']==0,read
  before=b.state(id);b.save(key+'-before.json',before)
  r=b.cli(['write',id,str(f),'--tab',tab])
  attempts=[r['returncode']]
  for retry in range(3):
   if r['returncode']!=3 or 'doc changed since last read' not in r['stderr']:break
   assert b.cli(['cat',id,'--tab',tab])['returncode']==0
   r=b.cli(['write',id,str(f),'--tab',tab]);attempts.append(r['returncode'])
  after=b.state(id);b.save(key+'-after.json',after)
  # Native payload has no account IDs; strip the synthetic tab ID from publication.
  state=summarize(after)
  row={'id':key,'markdown':md,'command':'gdoc write DOC specimen.md --tab TAB --account PERSONAL','returncode':r['returncode'],'state':state}
  row['stdout']=r['stdout'].replace(id,'DOC').replace(tab,'TAB')
  row['stderr']='\n'.join(line for line in r['stderr'].splitlines() if line.startswith('ERR:'))
  row['attempt_returncodes']=attempts
  out.append(row);(b.ROOT/'hunt/live-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
  print(key,r['returncode'],repr(state['text']),state['tables'],flush=True)
if __name__=='__main__':main()
