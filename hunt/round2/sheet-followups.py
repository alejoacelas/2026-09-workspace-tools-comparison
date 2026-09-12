"""Synthetic Sheets follow-ups, explicitly personal. Writes only Data rows 200–350.
No collection edits, sharing, deletion, or upstream changes. Requires live auth.
Run with ~/.local/share/uv/tools/workspace-mcp/bin/python.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hunt"))
import live as b
from googleapiclient.discovery import build

OUT = Path(__file__).with_suffix(".json")
service = build("sheets", "v4", credentials=b.creds)
sid = json.loads((b.LOCAL / "r2-sheets-ledger.json").read_text())["id"]
result = {"pin": "dbfa4c34bfa699ee8dd9839da85eea1fac177d44", "verification": {}, "cases": []}

def save():
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

def get(a1, mode="FORMATTED_VALUE"):
    return service.spreadsheets().values().get(spreadsheetId=sid, range="Data!" + a1,
        valueRenderOption=mode).execute().get("values", [])

def put(a1, values, mode="RAW"):
    b.identity()
    return service.spreadsheets().values().update(spreadsheetId=sid, range="Data!" + a1,
        valueInputOption=mode, body={"values": values}).execute()

def native(a1):
    data = service.spreadsheets().get(spreadsheetId=sid, ranges=["Data!" + a1],
        includeGridData=True, fields="sheets(data(rowData(values(userEnteredValue,effectiveValue,formattedValue))))").execute()
    return data["sheets"][0]["data"][0].get("rowData", [])

def record(key, **data):
    result["cases"].append({"id": key, **data})
    save()
    print(key, json.dumps(data, ensure_ascii=False)[:450], flush=True)

def file_case(key, line, suffix, start, expected, classification, user=False):
    path = b.LOCAL / ("r2-sheet-followup-" + key + suffix)
    path.write_bytes(line.encode("utf-8")); path.chmod(0o600)
    args = ["cells", sid, f"Data!A{start}", "--file", str(path)]
    if user:
        args.append("--user-entered")
    response = b.cli(args)
    actual = get(f"A{start}:E{start+3}")
    record(key, input=line, expected=expected, actual=actual,
           returncode=response["returncode"], matches=actual == expected,
           classification=classification)

def main():
    b.identity()
    result["verification"] = {"tsv_crlf": get("A7:B8"), "csv_crlf": get("A13:B14")}
    assert result["verification"]["tsv_crlf"] == [["Item", "Value\r"], ["Budget", "100\r"]]
    assert result["verification"]["csv_crlf"] == [["Item", "Value"], ["Budget", "100"]]
    # Independently evaluated spreadsheet formulas expose the invisible suffix.
    formulas = [[
        '=EXACT(B8,"100")', '=EXACT(B14,"100")',
        '=IFERROR(MATCH("Value",A7:B7,0),"not found")',
        '=IFERROR(MATCH("Value",A13:B13,0),"not found")', '=LEN(B8)',
    ], ['=LEN(B14)', '=EXACT(A25,"Item")', '=LEN(A25)']]
    put("D200", formulas, "USER_ENTERED")
    result["crlf_formula_effect"] = {"formulas": formulas, "values": get("D200:H201", "UNFORMATTED_VALUE")}
    assert result["crlf_formula_effect"]["values"][0] == [False, True, "not found", 2, 4]
    save()
    print("CRLF independent formulas", result["crlf_formula_effect"]["values"], flush=True)

    file_case("csv-utf8-bom", "\ufeffItem,Value\nBudget,100\n", ".csv", 210,
              [["Item", "Value"], ["Budget", "100"]], "confirmed BOM retention; same root case as initial sweep")
    file_case("quoted-tsv-tab", 'Item\tValue\n"North\tSouth"\t100\n', ".tsv", 216,
              [["Item", "Value"], ["North\tSouth", "100"]], "quoted TSV dialect unsupported; do not count as a promised CSV failure")
    file_case("quoted-tsv-newline", 'Item\tValue\n"North\nSouth"\t100\n', ".tsv", 222,
              [["Item", "Value"], ["North\nSouth", "100"]], "quoted TSV dialect unsupported; same quoting boundary")
    file_case("csv-quoted-tab-control", 'Item,Value\n"North\tSouth",100\n', ".csv", 228,
              [["Item", "Value"], ["North\tSouth", "100"]], "control")
    file_case("raw-identifier-control", "Code,Value\n00123,=1+2\n", ".csv", 234,
              [["Code", "Value"], ["00123", "=1+2"]], "control: RAW preserves literal identifiers and formula-like strings")
    file_case("entered-coercion-control", "Code,Value\n00123,=1+2\n", ".csv", 240,
              [["Code", "Value"], ["123", "3"]], "control: requested USER_ENTERED coercion", user=True)

    # Seed text containing legal cell-internal separators, then compare read modes.
    embedded = [["North\nSouth", "A\tB", "00123"]]
    put("A250", embedded)
    plain = b.cli(["cat", sid, "--tab", "Data", "--range", "A250:C250", "--plain"])
    structured = b.cli(["cat", sid, "--tab", "Data", "--range", "A250:C250", "--json"])
    payload = json.loads(structured["stdout"])
    record("json-embedded-separators-control", expected=embedded, actual=payload["values"],
           returncode=structured["returncode"], matches=payload["values"] == embedded,
           classification="control: JSON preserves in-cell newline/tab text")
    path = b.LOCAL / "r2-sheet-followup-readback.tsv"
    path.write_bytes(plain["stdout"].encode()); path.chmod(0o600)
    writeback = b.cli(["cells", sid, "Data!A256", "--file", str(path)])
    record("plain-read-write-separators", expected=embedded, exported=plain["stdout"], actual=get("A256:C256"),
           returncodes=[plain["returncode"], writeback["returncode"]],
           classification="documented lossy display: _format_sheet_tsv replaces embedded tabs/newlines with spaces")

    # Formula and typed values: preserve native source; write readback elsewhere.
    put("A270", [["=1+2", 1234.5, True, "00123"]])
    put("A270", [["=1+2"]], "USER_ENTERED")
    sheet_id = service.spreadsheets().get(spreadsheetId=sid, fields="sheets(properties(sheetId,title))").execute()["sheets"][0]["properties"]["sheetId"]
    b.identity()
    service.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": [{"repeatCell": {
        "range": {"sheetId": sheet_id, "startRowIndex": 269, "endRowIndex": 270, "startColumnIndex": 1, "endColumnIndex": 2},
        "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}},
        "fields": "userEnteredFormat.numberFormat"}}]}).execute()
    source = native("A270:D270")
    read = b.cli(["cat", sid, "--tab", "Data", "--range", "A270:D270", "--json"])
    values = json.loads(read["stdout"])["values"]
    argv = ["cells", sid, "Data!A280"]
    for value in values[0]:
        argv.extend(["-v", str(value)])
    written = b.cli(argv)
    target = native("A280:D280")
    record("formula-read-write", source_cell=source[0]["values"][0], exported_value=values[0][0],
           target_cell=target[0]["values"][0], returncodes=[read["returncode"], written["returncode"]],
           classification="capability boundary: formatted-value reads do not carry formula source; default RAW writes store display string")
    record("typed-values-read-write", source_cells=source[0]["values"][1:], exported_values=values[0][1:],
           target_cells=target[0]["values"][1:], returncodes=[read["returncode"], written["returncode"]],
           classification="capability boundary: formatted JSON values are strings, not a typed-cell snapshot")
    result["summary"] = {"followup_cases": len(result["cases"]), "crlf_family_count": 1,
                         "scope": "Data rows200–280 only; original rows7–14 read without changes; ten cases plus independent CRLF formulas"}
    b.save("r2-sheet-followups-native.json", {"source_typed": source, "target_typed": target,
           "formulas": native("D200:H201")})
    save()

if __name__ == "__main__":
    main()
