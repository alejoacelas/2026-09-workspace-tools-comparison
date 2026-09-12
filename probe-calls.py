"""Count API execute boundaries with synthetic responses; never contact Google.

Run with either checkout's Python and pass gdoc or workspace. Auth wrappers and
local state persistence are excluded. This is not a live API or latency test.
"""
import asyncio
import contextlib
import inspect
import io
import json
from pathlib import Path
import sys
from unittest.mock import Mock, patch

DOC = '1SyntheticOfficeComparisonDocument0123456789'
MIME = 'application/vnd.google-apps.document'
SHEET_MIME = 'application/vnd.google-apps.spreadsheet'
BODY = {'content': [{'startIndex': 1, 'endIndex': 13, 'paragraph': {
    'elements': [{'startIndex': 1, 'endIndex': 13, 'textRun': {'content': 'Hello world\n'}}],
    'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}}}]}
DOCUMENT = {'documentId': DOC, 'revisionId': 'rev1', 'title': 'Example', 'body': BODY,
    'tabs': [{'tabProperties': {'tabId': 't.0', 'title': 'Tab 1'}, 'documentTab': {'body': BODY}}]}


def fake_service(mime=MIME):
    service, calls = Mock(), []
    responses = {
        'files.get': {'id': DOC, 'name': 'Example', 'version': '1', 'mimeType': mime,
                      'modifiedTime': '2026-09-01T00:00:00Z', 'owners': []},
        'files.export_media': b'Hello world\n',
        'files.create': {'id': DOC, 'name': 'Example', 'version': '1', 'mimeType': MIME},
        'comments.list': {'comments': []},
        'permissions.create': {'id': 'p1', 'role': 'reader', 'type': 'user'},
        'documents.get': DOCUMENT,
        'documents.batchUpdate': {'replies': [{'replaceAllText': {'occurrencesChanged': 1}}]},
        'spreadsheets.get': {'properties': {'title': 'Data'}, 'sheets': [{'properties': {
            'sheetId': 0, 'title': 'Sheet1', 'index': 0, 'gridProperties': {'rowCount': 100, 'columnCount': 26}}}]},
        'spreadsheets.values.get': {'range': 'Sheet1!A1:B1', 'values': [['A', 'B']]},
        'spreadsheets.values.update': {'updatedRange': 'Sheet1!A1:B1', 'updatedCells': 2,
                                      'updatedData': {'values': [['A', 'B']]}},
    }
    for path, response in responses.items():
        target = service
        for part in path.split('.'):
            target = getattr(target, part).return_value
        def execute(*args, _path=path, _response=response, **kwargs):
            calls.append(_path)
            return _response
        target.execute.side_effect = execute
    return service, calls


def gdoc_cases():
    from gdoc.cli import build_parser
    from gdoc.state import DocState
    cases = [('read_doc', ['cat', DOC], MIME),
             ('read_doc_comments', ['cat', DOC, '--comments'], MIME),
             ('replace_phrase', ['edit', DOC, 'Hello', 'Hi'], MIME),
             ('read_sheet', ['cat', DOC, '--range', 'A1:B1'], SHEET_MIME),
             ('write_sheet', ['cells', DOC, 'A1:B1', '-v', 'A', '-v', 'B'], SHEET_MIME),
             ('share_one', ['share', DOC, 'reviewer@example.com'], MIME)]
    results = []
    for name, argv, mime in cases:
        for mode in ('warm', 'first', 'quiet'):
            service, calls = fake_service(mime)
            with contextlib.ExitStack() as stack:
                for module in ('drive', 'comments'):
                    stack.enter_context(patch(f'gdoc.api.{module}.get_drive_service', return_value=service))
                stack.enter_context(patch('gdoc.api.docs.get_docs_service', return_value=service))
                stack.enter_context(patch('gdoc.api.sheets.get_sheets_service', return_value=service))
                stack.enter_context(patch('gdoc.state.load_state', return_value=None if mode == 'first' else DocState(last_version=1, last_read_version=1)))
                stack.enter_context(patch('gdoc.state.save_state'))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                args = build_parser().parse_args(argv + (['--quiet'] if mode == 'quiet' else []))
                assert args.func(args) == 0
            results.append({'case': name, 'mode': mode, 'count': len(calls), 'requests': calls})
    expected = {'read_doc': (3, 4, 2), 'read_doc_comments': (4, 5, 3),
                'replace_phrase': (6, 7, 4), 'read_sheet': (4, 5, 3),
                'write_sheet': (4, 5, 2), 'share_one': (3, 4, 1)}
    for name, counts in expected.items():
        assert tuple(r['count'] for r in results if r['case'] == name) == counts
    return results


async def workspace_cases():
    from gdocs import docs_tools
    from gsheets import sheets_tools
    from gdrive import drive_tools
    common = {'user_google_email': 'user@example.com'}
    cases = [
        ('read_doc', docs_tools.get_doc_as_markdown, {'document_id': DOC, 'include_comments': False}, 'double'),
        ('read_doc_comments', docs_tools.get_doc_as_markdown, {'document_id': DOC}, 'double'),
        ('replace_phrase', docs_tools.find_and_replace_doc, {'document_id': DOC, 'find_text': 'Hello', 'replace_text': 'Hi'}, 'single'),
        ('replace_ten_phrases', docs_tools.batch_update_doc, {'document_id': DOC, 'operations': [
            {'type': 'find_replace', 'find_text': 'placeholder' + str(i), 'replace_text': 'value'} for i in range(10)]}, 'single'),
        ('read_sheet', sheets_tools.read_sheet_values, {'spreadsheet_id': DOC, 'range_name': 'Sheet1!A1:B1'}, 'single'),
        ('write_sheet', sheets_tools.modify_sheet_values, {'spreadsheet_id': DOC, 'range_name': 'Sheet1!A1:B1', 'values': [['A', 'B']]}, 'single'),
        ('create_markdown_doc', drive_tools.import_to_google_doc, {'file_name': 'Example.md', 'content': '# Hello'}, 'single'),
    ]
    results = []
    for name, tool, kwargs, kind in cases:
        service, calls = fake_service('application/vnd.google-apps.folder' if name == 'create_markdown_doc' else MIME)
        fn = inspect.unwrap(getattr(tool, 'fn', tool))
        injected = {'drive_service': service, 'docs_service': service} if kind == 'double' else {'service': service}
        result = await fn(**injected, **common, **kwargs)
        assert 'Error' not in str(result), result
        results.append({'case': name, 'count': len(calls), 'requests': calls})
    assert [r['count'] for r in results] == [1, 2, 1, 3, 1, 1, 2]
    return results


if __name__ == '__main__':
    choice = sys.argv[1]
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / 'repos' / ('gdoc' if choice == 'gdoc' else 'google-workspace-mcp')))
    result = gdoc_cases() if choice == 'gdoc' else asyncio.run(workspace_cases())
    print(json.dumps(result, indent=2))
