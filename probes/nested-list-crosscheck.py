"""Capture complete gdoc tab-writer requests offline for 2/4-space children."""
import json
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'repos/gdoc'))
from gdoc.api.docs import insert_markdown_into_tab
from gdoc.mdparse import parse_markdown

rows=[]
for spaces in [2,4]:
    markdown='- Parent\n'+' '*spaces+'- Child\n- Peer'
    parsed=parse_markdown(markdown)
    service=MagicMock()
    doc={'revisionId':'probe-revision','tabs':[{'tabProperties':{'tabId':'probe-tab','title':'Probe'},'documentTab':{'body':{'content':[{'endIndex':2,'paragraph':{'elements':[{'textRun':{'content':'\n'}}]}}]}}}]}
    with patch('gdoc.api.docs.get_document_with_tabs',return_value=doc),patch('gdoc.api.docs.get_docs_service',return_value=service):
        insert_markdown_into_tab('probe-doc','probe-tab',markdown,replace=True)
    calls=service.documents.return_value.batchUpdate.call_args_list
    bodies=[call.kwargs['body'] for call in calls]
    assert len(bodies)==1
    emitted=next(r['insertText']['text'] for r in bodies[0]['requests'] if 'insertText' in r)
    assert '\t'*(spaces//2)+'Child' in emitted
    rows.append({'indent_spaces':spaces,'markdown':markdown,'parsed_text':parsed.plain_text,'complete_writer_batches':bodies,'observation':'Child tab(s) survive the complete native writer; no subsequent cleanup batch for this no-table fixture.'})
(ROOT/'evidence/nested-list-crosscheck.json').write_text(json.dumps(rows,indent=2)+'\n')
print('2/4-space complete native writer requests captured; one batch each; tabs preserved')
