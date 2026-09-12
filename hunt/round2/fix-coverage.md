# Existing repair coverage for H10–H19

H16 is already covered by the pending native-boundary patch in PR #66: its generic non-text barrier also stops matches across person and file chips. I executed that PR head's actual search functions on synthetic chip-shaped input and confirmed the refusal. The patch is **open, not installed in the tested gdoc pin**. The other nine findings are not corrected by the reviewed patches. Several are additional cases within existing repair areas, rather than wholly new bug families.

This review compares the ten public synthetic findings with the existing campaign's consolidated repair groups, without copying its private specimens. It checks public PR code as well as titles. Current open PRs and heads were read through `gh` on **2026-09-12, 19:25–19:30 UTC**. The tested application remains pinned to `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. A patch-level search check is narrower than a full live CLI replay of the patch.

| Finding | Relationship to earlier repair areas | Actual patch coverage and remaining work |
| --- | --- | --- |
| **H10 — selected-tab read omits chips** | Additional native-element export case within Markdown serialization work (G05); subsequent destructive reconstruction also relates to G04. Reading and deletion are separate contracts. | **No read fix found.** The inspected open heads retain `get_tab_text`, `_runs_markdown`, and `_extract_paragraphs_text`. #62/#65 add reconstruction guards; they do not make chip labels appear in selected-tab output. #66 changes matching, not export. Add native person/date/file read fixtures. |
| **H11 — TSV CRLF leaves carriage returns** | No matching repair group in the reviewed fourteen-group consolidated summary. This is a file-record parsing case. | **No fix found.** `_read_cell_rows` still uses `open(..., encoding="utf-8", newline="")` followed by `line.rstrip("\n").split("\t")`. The final CR survives. Sheets feature PR [#20](https://github.com/LucaDeLeo/gdoc/pull/20) is merged; its existence does not establish handling of Windows TSV. Keep LF TSV and CRLF CSV as controls. |
| **H12 — ten-digit account becomes a list** | Additional block-marker grammar case in G05. Distinct input trigger, not a new overarching parser family. | **No parser fix found.** The current open parser heads retain the unbounded numbered marker `\d+`; #60 also leaves that pattern and `parse_markdown` unchanged. #62's guard examines existing native state, so it is not a repair for malformed interpretation of newly supplied Markdown in a blank tab. |
| **H13 — bracketed link label becomes literal Markdown** | G05 round-trip agreement; related shared parser work to G06, but nested label brackets differ from balanced destination parentheses. | **No parser/export fix found.** The link pattern still ends the label at the first `]`. The selected-tab exporter can emit the same failing syntax. #62 may refuse some existing-document round trips; that is not successful link creation or a grammar repair. |
| **H14 — entity changes URL query key** | Additional link-destination parsing case; suitable for the shared link-parser repair area rather than a separate general reconstruction project. | **No fix found.** The reviewed heads retain the link extraction behavior without decoding the destination's Markdown entity. #60's parser changes concern code delimiters and strikethrough, not this path. Link-label text checks alone cannot test this defect: assert the native URL. |
| **H15 — merged label targets covered column** | Extends G02 target resolution. The old family emphasizes ambiguity/identity; this case is span-aware geometry even with a unique label. | **No fix found.** `resolve_cell_range` remains unchanged across the reviewed open heads: default target is `ci + 1`, without advancing past `columnSpan`. Merged table feature support or native-range barriers do not correct that choice. Test span two and span three alongside explicit-column controls. |
| **H16 — phantom match deletes chip** | **Existing G03 mechanism:** a deletion range spans an omitted native element. New person/file-chip witnesses strengthen the same repair boundary. | **Confirmed patch-level coverage in [#66](https://github.com/LucaDeLeo/gdoc/pull/66), still OPEN.** It splits whenever an inline element has no `textRun`, not merely when it is an image or footnote. Executed person/rich-link/date-shaped probes all return no match at the reviewed head; the tested main pin returns a spanning range. Existing #66 fixture vocabulary/tests cover images and footnotes, not chips, so chip-specific regression fixtures are still useful. This does not establish protection for whole-cell deletion or matches across whole tables. |
| **H17 — exact Greek character not found** | Related to G10 text transformation, but contextual final-sigma folding changes match semantics rather than expanding offsets. Mapping transformed offsets alone does not repair it. | **No fix found.** #61 changes searched containers but retains whole-string `.lower()` on both sides. #66 adds native-element boundaries and retains that transformation. Preserve exact matches before fallback; any case-folding design needs separate semantic and coordinate tests. Native Google finds the literal uppercase character in the independently replayed fixture. |
| **H18 — comment becomes malformed TSV records** | No matching serialization repair in the reviewed consolidated groups. G11 concerns locating/creating anchors, not formatting comment-list stdout. | **No fix found.** #56/#61/#62 touch `cmd_comments`, but its plain-output branch still interpolates raw content between tab delimiters. Other inspected heads retain it. Native comment content and JSON are correct. A quoting-aware TSV reader returns two logical records, of five and two fields; a properly quoted control returns one record with five fields. This is output schema corruption, not stored comment loss. |
| **H19 — UTF-8 signature becomes header content** | No matching group in the reviewed summary. Shares file-reader code with H11, but encoding-signature handling and line endings require separate assertions. | **No fix found.** `_read_cell_rows` still decodes file input as `utf-8`, preserving initial U+FEFF as data. CRLF stripping alone would not repair this. The native Google CSV import control consumes the same signature correctly. Assert exact header contents and formula behavior, not a screenshot of an apparently normal header. |

The same-input live Workspace controls pass H12–H14's targeted text/link assertions, with the separately recorded extra trailing paragraphs; see [workspace-markdown.md](workspace-markdown.md). That establishes comparative behavior on those inputs, not correctness of either application on arbitrary Markdown.

## Reviewed public patch heads

These were the complete open-PR list returned during this review. Relevant functions were compared with the tested pin using parsed Python syntax or inspected directly. In particular, changes to comments code in #56/#61/#62 were inspected rather than dismissed from their titles. Parser changes in #60 were inspected as a diff; they leave these three H12–H14 mechanisms intact.

| Open PR | Exact reviewed head |
| --- | --- |
| [#54](https://github.com/LucaDeLeo/gdoc/pull/54) | `34f31a0c0a583204d6d80f75edb8b81b76d55981` |
| [#55](https://github.com/LucaDeLeo/gdoc/pull/55) | `129c821c50fcdb1752db9babc6a595db94395299` |
| [#56](https://github.com/LucaDeLeo/gdoc/pull/56) | `6057b799b697bfcd056b36053bdac775571a559e` |
| [#58](https://github.com/LucaDeLeo/gdoc/pull/58) | `8b7a386194b5279f4edb56e90d7024a9794e60c5` |
| [#60](https://github.com/LucaDeLeo/gdoc/pull/60) | `b63636493bb71e75a742fee1aee3253ea21c44d8` |
| [#61](https://github.com/LucaDeLeo/gdoc/pull/61) | `13703e0136dfef49f77af86d421d5188e2d27e88` |
| [#62](https://github.com/LucaDeLeo/gdoc/pull/62) | `90fe8b1b81ac26d4d63fd7a9433fca093eb8876a` |
| [#63](https://github.com/LucaDeLeo/gdoc/pull/63) | `df6309bb6f62bc4a17798dfdb0fb788476a643c2` |
| [#64](https://github.com/LucaDeLeo/gdoc/pull/64) | `6335ce046293db48b74d5e50a8897990af767163` |
| [#65](https://github.com/LucaDeLeo/gdoc/pull/65) | `c9d7bdb5735f1836547deccb1160822ada76e3a3` |
| [#66](https://github.com/LucaDeLeo/gdoc/pull/66) | `70f7184305d501eff7d940ba6c1ea00ff6a53ccc` |

Historical feature PRs [#19](https://github.com/LucaDeLeo/gdoc/pull/19), [#20](https://github.com/LucaDeLeo/gdoc/pull/20), [#29](https://github.com/LucaDeLeo/gdoc/pull/29), and [#32](https://github.com/LucaDeLeo/gdoc/pull/32) were confirmed merged. The current pinned implementations and live failures remain the evidence for the shortcomings; a merged feature title is not a fix claim. Local PR snapshots remain at `evidence/gdoc-prs/`.

## Reproduce the confirmed #66 coverage without Google credentials

This is the executed check reduced to a standalone form. It fetches public code at an immutable revision, extracts the three actual search functions, and supplies synthetic API-shaped input. It makes no Google calls or filesystem changes. The date-shaped case tests the generic barrier only; the independently measured destructive H16 findings are person and file chips.

```python
import ast
import pathlib
import subprocess

pin = "70f7184305d501eff7d940ba6c1ea00ff6a53ccc"
patched = subprocess.check_output([
    "gh", "api", f"repos/LucaDeLeo/gdoc/contents/gdoc/api/docs.py?ref={pin}",
    "-H", "Accept: application/vnd.github.raw+json",
], text=True)
baseline = pathlib.Path("repos/gdoc/gdoc/api/docs.py").read_text()
names = {"_utf16_len", "_collect_segments", "find_text_in_document"}
for label, source in [("tested main", baseline), ("PR 66", patched)]:
    functions = [ast.get_source_segment(source, node)
                 for node in ast.parse(source).body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {}
    exec("\n\n".join(functions), namespace)
    for kind in ["person", "richLink", "dateElement"]:
        body = {"content": [{"paragraph": {"elements": [
            {"startIndex": 1, "endIndex": 8,
             "textRun": {"content": "Before "}},
            {"startIndex": 8, "endIndex": 9, kind: {}},
            {"startIndex": 9, "endIndex": 17,
             "textRun": {"content": " after.\n"}},
        ]}}]}
        result = namespace["find_text_in_document"](
            None, "Before  after", body=body)
        expected = [] if label == "PR 66" else [
            {"startIndex": 1, "endIndex": 15}]
        assert result == expected, (label, kind, result)
        print(label, kind, result)
```

Use **ten additional demonstrated cases** when describing H10–H19. Avoid “ten entirely new bug families,” “no fixes exist,” or “#66 is installed and fixes chips.” The defensible distinction is one demonstrated pending patch fix, several related repair areas, and additional unaddressed format/encoding cases within the reviewed scope.
