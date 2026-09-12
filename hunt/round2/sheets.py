"""CSV/TSV interoperability checks through the real pinned gdoc cells CLI."""
import csv,io,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import live as b
from googleapiclient.discovery import build
sheets=build('sheets','v4',credentials=b.creds)
b.identity();id=sheets.spreadsheets().create(body={'properties':{'title':'Synthetic gdoc tabular import checks'},'sheets':[{'properties':{'title':'Data'}}]}).execute()['spreadsheetId'];b.save('r2-sheets-ledger.json',{'id':id})
cases=[
 ('tsv-lf','Item\tValue\nBudget\t100\n','.tsv',[['Item','Value'],['Budget','100']],False),
 ('tsv-crlf','Item\tValue\r\nBudget\t100\r\n','.tsv',[['Item','Value'],['Budget','100']],False),
 ('csv-crlf','Item,Value\r\nBudget,100\r\n','.csv',[['Item','Value'],['Budget','100']],False),
 ('tsv-cr','Item\tValue\rBudget\t100\r','.tsv',[['Item','Value'],['Budget','100']],False),
 ('csv-bom','\ufeffItem,Value\nBudget,100\n','.csv',[['Item','Value'],['Budget','100']],False),
 ('tsv-leading-zero','Code\tValue\n00123\t00100\n','.tsv',[['Code','Value'],['00123','00100']],False),
 ('csv-quoted-newline','Item,Value\n"North\nSouth",100\n','.csv',[['Item','Value'],['North\nSouth','100']],False),
 ('tsv-quoted-newline','Item\tValue\n"North\nSouth"\t100\n','.tsv',[['Item','Value'],['North\nSouth','100']],False),
 ('csv-quoted-comma','Item,Value\n"North, South",100\n','.csv',[['Item','Value'],['North, South','100']],False),
 ('csv-quotes','Item,Value\n"The ""North"" team",100\n','.csv',[['Item','Value'],['The "North" team','100']],False),
 ('raw-formula','Item,Value\nTotal,=1+2\n','.csv',[['Item','Value'],['Total','=1+2']],False),
 ('entered-formula','Item,Value\nTotal,=1+2\n','.csv',[['Item','Value'],['Total','3']],True),
]
results=[]
for i,(key,data,suffix,expected,user) in enumerate(cases):
 start=1+i*6;f=b.LOCAL/('r2-'+key+suffix);f.write_bytes(data.encode())
 argv=['cells',id,f'Data!A{start}','--file',str(f)]
 if user:argv.append('--user-entered')
 r=b.cli(argv)
 actual=sheets.spreadsheets().values().get(spreadsheetId=id,range=f'Data!A{start}:C{start+4}').execute().get('values',[])
 # Leading headers/values compare exact chars. Numeric FORMATTED_VALUE strings are intended.
 results.append({'id':key,'input':data,'expected':expected,'actual':actual,'returncode':r['returncode'],'matches':actual==expected,'stderr':'\n'.join(x for x in r['stderr'].splitlines() if x.startswith('ERR:'))})
 print(key,r['returncode'],actual==expected,repr(actual),flush=True)
(Path(__file__).with_name('sheets-results.json')).write_text(json.dumps({'pin':'dbfa4c34','cases':results},indent=2,ensure_ascii=False)+'\n')
b.save('r2-sheets-native.json',sheets.spreadsheets().get(spreadsheetId=id,includeGridData=True).execute())
