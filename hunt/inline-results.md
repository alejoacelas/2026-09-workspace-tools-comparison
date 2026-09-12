# Inline Markdown hunt

**Four reproducible candidates deserve live confirmation:** optional link titles contaminate the destination, multi-backtick code spans corrupt text, a trailing backslash defeats code-span recognition, and Markdown delimiters inside code prematurely close enclosing emphasis. These are ordinary document-conversion failures in gdoc's native Markdown path, not security findings.

The [executable probe](inline-probe.py) ran **24 synthetic inputs** against gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44` and Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564`. gdoc matched the selected text/style assertions on 7 and differed on 17; Workspace matched 23 and differed on 1. These deliberately chosen inputs are not a representative sample, and the differences are **not 17 distinct bugs**. [Full requests and observations](inline-results.json)

| Candidate | Input | Expected | gdoc generated result |
|---|---|---|---|
| Optional link title becomes URL text | ` Read [Policy](https://example.com/policy "Policy handbook"). ` | ` Read Policy. `; link URL excludes title | ` Read Policy. `; link URL includes title |
| Multi-backtick code span | ``` Use ``a`b`` now. ``` | `` Use a`b now. ``; complete a`b in code font | ``` Use `ab`` now. ```; only a in code font |
| Backslash at end of code | `` Use `C:\temp\` now. `` | ` Use C:\temp\ now. `; complete path in code font | `` Use `C:\temp` now. ``; no code font; trailing backslash lost |
| Code delimiter closes enclosing emphasis | `` **Use `a**b` today** `` | ` Use a**b today `; whole phrase bold; a**b in code font | `` Use `ab` today** ``; only prefix bold; no code font |

Exact URLs and styles are in JSON cases `link_title`, `double_backtick`, `code_trailing_slash`, and `bold_contains_code_marker`.

## Why these are useful regression cases

- **Link syntax is being partially recognized, not simply unsupported.** gdoc removes link markup and emits a native Google URL, but includes the optional title in that URL. The title does not belong in the target. The related angle-bracket destination case retains literal `<` and `>` in the URL, and entity-encoded query delimiters remain encoded as `&amp;`.
- **Code spans should contain literal text.** The parser recognizes only single-backtick patterns, and its escape-masking pass runs before it knows which text belongs to code. These specimens expose delimiter-run handling and the interaction between backslashes and code recognition. A single-backtick code span containing a trailing backslash is complete and valid; backslash does not escape its closing backtick inside code.
- **Inline precedence matters even with balanced, unambiguous source.** In the bold/code specimen, the pair of asterisks inside code is literal. The outer bold regex incorrectly consumes it as the closing emphasis marker. This is not the previously observed adjacent-emphasis ambiguity or loss of existing native styles: the input itself contains all the intended styles, and the converter misparses them before Google is involved.

All four reach `parse_markdown` and then native Docs requests through `gdoc write --tab` and `gdoc insert`. `gdoc edit` also invokes the parser for replacements, but a live tab-write reproduction does not by itself certify every replacement context or `suggest` path. Whole-document Drive import uses a different converter and is outside this test. Images were not promoted: the native parser's lack of native-image creation is already a known route limitation, not a fresh defect demonstrated here.

## Nonfailures and less decisive differences

All seven explicit controls passed in **both** implementations: ordinary inline link, escaped square brackets in a link label, an all-spaces code span, literal backslash inside code away from the closing delimiter, literal `&amp;` inside code, escaped ampersand outside code, and literal bold markers inside code. Thus code/backslashes/emphasis are not universally broken; their interactions are the trigger.

Other gdoc differences include unescaped nested brackets in a link label, a bracket inside a code-formatted link label, trimming the optional single surrounding space in code spans, entity decoding, angle-bracket link destinations, and the triple-backtick variant. They are recorded, but several are variants of the same small-regex grammar limitations rather than separate product failures.

The one Workspace difference is `[draft]()` retaining the label but not emitting an empty native URL. That is **not promoted as a Workspace bug**: a syntactically valid empty Markdown destination has no useful Google Docs hyperlink target without a base-document URL policy. The report does not count that ambiguity as a strong failure.

## Independence, deduplication and limits

The oracle reads visible text and inline style targets from `markdown-it` CommonMark tokens and compares them with emitted Google requests using the existing UTF-16 replayer. This is independent of gdoc's implementation. **Workspace uses the same Markdown parser as the oracle**, so its agreement is a compatibility check, not an independent vote that settles all semantics. The observer checks inline targets and URLs; it does not model Google's entire style engine or prove which malformed URL Google will accept, reject or normalize.

The existing campaign's consolidated and narrative reports were reviewed for overlap. The new cases sit within the broad existing Markdown/inline-formatting family; they are **additional concrete parser regressions**, not newly discovered categories of document risk. No private campaign text, document content, rates or identifiers are reproduced here. Existing known cases—intraword underscores, balanced URL parentheses, native bold loss, Unicode indexing, adjacent emphasis and literal block markers—were excluded from the promoted set.

No network or Google writes occur in this probe. Root's separate live confirmation writes disposable synthetic documents and captures Google's resulting native state; those observations should take precedence over predictions about visible behavior.

Reproduce:

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/inline-probe.py
```
