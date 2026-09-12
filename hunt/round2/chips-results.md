# Smart-chip read omission and cross-chip replacement

**Two related failures are confirmed live in pinned gdoc: selected-tab reads omit person/date/file chips, and a replacement can match across an omitted chip and delete it.** Ordinary text edits next to a chip do not generally remove it. These findings concern native non-text elements, not malformed Markdown.

Versions: gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`; Workspace `54b1c56f7f9912ce32681460d7ca38f9c2a37564`. Every document is a newly created synthetic scratch fixture. The only genuine person reference is the explicitly authorized account's self-chip; names, email and resource IDs are anonymized in public evidence and retained only in ignored `.local-hunt/r2-chips*` files.

## Read omission: a bounded seven-context specimen

The native API first verified four `person` elements, one `dateElement`, and one `richLink`. The seven contexts were ordinary text, a person in a sentence, a person alone after a label, a person beside bold text, a person beside linked text, a date, and a file chip. Both gdoc read routes returned exit 0.

| Native content | Plain `gdoc cat DOC` | `gdoc cat DOC --tab TAB` | Workspace `get_doc_as_markdown` with explicit tab |
|---|---|---|---|
| `Example Owner owns budget.` as ordinary text | Preserved | Preserved | Preserved |
| Person chip, in four contexts | Preserved as a mailto link | Chip name and email completely absent | Preserved as a mailto link |
| `Before` in bold beside a person chip | Bold word and chip preserved | Bold word preserved; chip omitted | Both preserved |
| Linked `Policy` beside a person chip | Link and chip preserved | Link preserved; chip omitted | Both preserved |
| Native date displaying `2030-01-02` | Date preserved | Date absent: `Date:  due.` | Date preserved |
| File chip with a synthetic document title | Title and target preserved | Both absent: `File:  attached.` | Both preserved |

This is **one read-omission family**, not separate bugs for each chip type. The ordinary text and adjacent styling controls show that the selected-tab reader is functioning and preserving some formatting while skipping non-text paragraph elements. An initial date insertion with an explicit timezone was rejected; omitting that optional field succeeded, and the final assertions use the confirmed native date element. [Native elements and exact anonymized read outputs](chips-results.json)

## Destructive replacement: the missing chip becomes an invisible gap

The live native document contains:

```text
Before [person or file chip] after.
```

The selected-tab read exposes:

```text
Before  after.
```

Then this command reports success:

```sh
gdoc edit DOC 'Before  after' 'Replacement' --tab TAB --account PERSONAL
```

Native verification finds **zero chips**, down from one, and text `Replacement.`. Both a person-chip fixture and a file-chip fixture reproduce it. The matcher joins `textRun` characters across intervening non-text elements, finds the synthetic phrase, and turns the corresponding non-contiguous characters into one contiguous deletion range that includes the chip. The caller did not supply the chip's visible name as part of the target.

The independent Google API reference is decisive: native `replaceAllText` with the same phrase on an equivalent fresh person-chip document reports **0 replacements and retains the chip**. A positive native control replacing the ordinary suffix `after` with `later` reports one replacement and retains the chip. [Native reference results](chips-oracle-results.json)

The actual Workspace MCP `find_and_replace_doc` tool was also run on a separate equivalent person-chip fixture. It reported **0 replacements**, retained the native chip, and returned a successful MCP result. Thus the comparison uses both the independent native reference and the competing app's exposed operation. [Workspace live mutation result](chips-workspace-edit-results.json)

| Fresh-fixture operation through gdoc | CLI result | Native chip count | Interpretation |
|---|---|---|---|
| Ordinary text-only `draft`→`final` | Exit 0 | 0→0 | Positive text control |
| Replace `draft` after person chip | Exit 0 | 1→1 | Ordinary adjacent edit retains chip |
| Replace `draft` before person chip | Exit 0 | 1→1 | Ordinary adjacent edit retains chip |
| Replace `draft` after file chip | Exit 0 | 1→1 | Ordinary adjacent edit retains chip |
| Replace synthetic `Before  after` across person chip | Exit 0 | **1→0** | Silent chip deletion |
| Replace synthetic `Before  after` across file chip | Exit 0 | **1→0** | Same mechanism, second native type |
| Target the person's actual visible chip name | Exit 3: no match | 1→1 | Safe refusal, feature gap |
| Append an adjacent sentence using `insert --position end` | Exit 0 | 1→1 | Append retains chip |

Chip counts establish retention/deletion; they do not certify every direct style field in the document. Full anonymized before/after elements are provided for review. [Eight executed mutation cases](chips-edits-results.json)

## Broader hypotheses, without inflating the bug count

A separate [offline matcher probe](chips-matching.py) exercised 12 cases. Eight synthetic native-element variants—person, date, file link, footnote reference, inline image, horizontal rule, page break, and column break—produce the same cross-element match. Four ordinary text controls behaved as expected: a real double-space phrase matches; a single space, intervening newline, or literal object-replacement character does not match that double-space phrase. [All bodies and returned ranges](chips-matching-results.json)

These are variants of the **same boundary-handling mechanism**, not eight newly established live failures. Only person and file deletion were live-tested here. Native footnote/image boundary behavior may overlap the existing campaign's broader boundary family; no private campaign content is reproduced. Their exact Google-side mutation outcomes remain unmeasured.

The read fixture was never used for the destructive tests. Every edit case had a separate fresh scratch document, an explicit selected-tab read baseline, and native before/after verification. There was no deletion of files, sharing, editing of ordinary office documents, or modification of the user-facing collection.

Reproduce read fixtures with `hunt/round2/chips.py`, edit fixtures with `hunt/round2/chips-edits.py`, and offline matching with `hunt/round2/chips-matching.py`, using Workspace's installed Python. The live scripts create additional scratch documents when rerun. They do not delete them.
