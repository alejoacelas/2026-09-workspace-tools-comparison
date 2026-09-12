"""Offline transfer tests inspired by public gdoc PRs; no Google requests.

Run with Workspace MCP's installed Python. Captures generated requests and tests
pure converters/credential handling with synthetic inputs and dummy credentials.
These assertions characterize pinned code; they are not expected-correct tests.
"""
import asyncio
import inspect
import json
import os
from pathlib import Path
import ssl
import sys
import tempfile
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'repos/google-workspace-mcp'))
sys.path.insert(0, str(ROOT / 'repos/gdoc'))
from gdoc.auth import _write_private
from gdoc.mdparse import parse_markdown, to_docs_requests
from auth.credential_store import LocalDirectoryCredentialStore
from core.utils import handle_http_errors
from gdocs import docs_tools
from gdocs.docs_helpers import create_find_replace_request
from gdocs.docs_markdown import convert_doc_to_markdown
from gdocs.docs_markdown_writer import markdown_to_docs_requests
from gdocs.managers.batch_operation_manager import BatchOperationManager
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import httplib2


def paragraph(text, start=1, **extra):
    end = start + len(text.encode('utf-16-le')) // 2
    return {'startIndex': start, 'endIndex': end, 'paragraph': {
        'elements': [{'startIndex': start, 'endIndex': end, 'textRun': {'content': text}}], **extra}}


def doc(body):
    return {'documentId': 'synthetic', 'revisionId': 'r1', 'tabs': [
        {'tabProperties': {'tabId': 't.0', 'title': 'One'}, 'documentTab': {'body': body}},
        {'tabProperties': {'tabId': 't.1', 'title': 'Two'}, 'documentTab': {'body': {'content': [paragraph('untouched\n')]}}}]}


def service_for(document):
    service = Mock()
    service.documents.return_value.get.return_value.execute.return_value = document
    service.documents.return_value.batchUpdate.return_value.execute.return_value = {'replies': []}
    return service


async def main():
    results = {}
    request = create_find_replace_request('old', 'new', True, 't.0')
    assert request == {'replaceAllText': {'containsText': {'text': 'old', 'matchCase': True}, 'replaceText': 'new', 'tabsCriteria': {'tabIds': ['t.0']}}}
    results['plain_replace_avoids_gdoc_extra_newline_and_markdown_resets'] = request

    rich_body = {'content': [paragraph('target\n'), {'startIndex': 8, 'endIndex': 20, 'table': {'rows': 1, 'columns': 1, 'tableRows': [{'tableCells': [{'content': [paragraph('cell\n', 11)]}]}]}}]}
    for name, body, markdown in [('rich_body', rich_body, 'new'), ('identical_plain', {'content': [paragraph('same\n')]}, 'same')]:
        service = service_for(doc(body))
        fn = inspect.unwrap(getattr(docs_tools.manage_doc_tab, 'fn', docs_tools.manage_doc_tab))
        result = await fn(service=service, user_google_email='synthetic@example.invalid', document_id='synthetic', action='populate_from_markdown', tab_id='t.0', markdown_text=markdown)
        batch = service.documents.return_value.batchUpdate.call_args.kwargs['body']
        assert batch['requests'][0].get('deleteContentRange')
        assert 'writeControl' not in batch
        assert result['success']
        results['populate_' + name] = {'result': result, 'batch': batch}

    service = service_for(doc({'content': [paragraph('same\n')]}))
    manager = BatchOperationManager(service)
    ok, message, metadata = await manager.execute_batch_operations('synthetic', [{'type': 'insert_text', 'text': 'x', 'index': 1, 'tab_id': 't.0'}])
    assert ok, message
    batch = service.documents.return_value.batchUpdate.call_args.kwargs['body']
    assert metadata['revision_before'] == 'r1' and 'writeControl' not in batch
    results['batch_revision_observed_but_not_enforced'] = {'revision_before': metadata['revision_before'], 'batch': batch}

    with tempfile.TemporaryDirectory() as tmp:
        store = LocalDirectoryCredentialStore(tmp)
        account = 'synthetic@example.invalid'
        path = Path(store._get_credential_path(account))
        path.write_text('{}')
        path.chmod(0o644)
        assert store.store_credential(account, Credentials('DUMMY_NOT_A_REAL_TOKEN'))
        mode = path.stat().st_mode & 0o777
        assert mode == 0o644
        results['existing_credentials_permissions'] = {'before': '0644', 'after': oct(mode), 'dummy_credentials_only': True}
        _write_private(path, '{}')
        assert path.stat().st_mode & 0o777 == 0o600
        results['gdoc_existing_credentials_permissions'] = {'before': '0644', 'after': '0600'}

    for name, exception in [('ssl', ssl.SSLError('synthetic')), ('connection_reset', ConnectionResetError('synthetic')), ('http_503', HttpError(httplib2.Response({'status': '503'}), b'{"error":{"message":"synthetic"}}'))]:
        attempts = 0
        @handle_http_errors('synthetic_read', is_read_only=True)
        async def flaky():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise exception
            return 'ok'
        with patch('core.utils.asyncio.sleep'):
            try:
                await flaky()
                recovered = True
            except Exception:
                recovered = False
        assert (attempts, recovered) == ((2, True) if name == 'ssl' else (1, False))
        results['retry_' + name] = {'attempts': attempts, 'recovered': recovered}

    cases = {'nested_list': '- parent\n  - child\n- peer', 'table': '| A | B |\n| --- | --- |\n| x | y |', 'strikethrough': '~~gone~~', 'image': '![Diagram](https://example.invalid/image.png)', 'heading_bold': '# **Heading**'}
    for name, md in cases.items():
        requests = markdown_to_docs_requests(md, tab_id='t.0')
        if name == 'nested_list':
            inserts = [r['insertText']['text'] for r in requests if 'insertText' in r]
            assert not any('\t' in text for text in inserts)
            assert sum('createParagraphBullets' in r for r in requests) == 1
        if name == 'table':
            assert not any('insertTable' in r for r in requests)
        if name == 'image':
            assert not any('insertInlineImage' in r for r in requests)
        results['markdown_' + name] = requests

    results['gdoc_nested_list_requests'] = to_docs_requests(parse_markdown(cases['nested_list']), 1)
    assert any('\tchild' in r.get('insertText', {}).get('text', '') for r in results['gdoc_nested_list_requests'])

    native = {'body': {'content': [paragraph('Heading\n', paragraphStyle={'namedStyleType': 'HEADING_1'}), paragraph('Item\n', 9, bullet={'listId': 'list1'})]}, 'lists': {'list1': {'listProperties': {'nestingLevels': [{'glyphType': 'GLYPH_TYPE_UNSPECIFIED', 'glyphSymbol': '●'}]}}}}
    md = convert_doc_to_markdown(native)
    assert '# Heading' in md and '- Item' in md, repr(md)
    results['heading_and_list_export'] = md
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
