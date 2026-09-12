"""Native Google CSV-import reference for a UTF-8 byte-order signature."""
import json,sys,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));import live as b
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
source='\ufeffItem,Value\nBudget,100\n';ledger=b.LOCAL/'r2-native-csv-ledger.json'
if ledger.exists():id=json.loads(ledger.read_text())['id']
else:
 b.identity();id=b.drive.files().create(body={'name':'Synthetic native CSV signature control','mimeType':'application/vnd.google-apps.spreadsheet'},media_body=MediaIoBaseUpload(io.BytesIO(source.encode()),mimetype='text/csv'),fields='id').execute()['id'];b.save(ledger.name,{'id':id})
s=build('sheets','v4',credentials=b.creds);actual=s.spreadsheets().values().get(spreadsheetId=id,range='A1:B2').execute().get('values',[])
assert actual[0][0]=='Item'
Path(__file__).with_suffix('.json').write_text(json.dumps({'input':source,'native_google_csv_import':actual,'header_matches':True},indent=2)+'\n')
