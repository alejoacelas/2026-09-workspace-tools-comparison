# Pull, local editing and push

**The ten bounded checks passed: ordinary text edits reached the correct document, filenames and title punctuation survived, and a multi-tab push refused safely while preserving both tabs.** No new defect was found. This does not reclassify the already known rich-document rebuild losses as safe.

Pinned gdoc: 0.21.0, `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`. The [live probe](local-roundtrip.py) created three synthetic Google Docs, used owner-only local fixture storage, and read native document state after pushes. The two single-tab documents contained simple text; one stayed untouched as a target-isolation control. The third had two tabs with distinct sentinel text. [Exact outcomes](local-roundtrip.json)

| Check | Observed result |
|---|---|
| Ordinary `pull` | File frontmatter contains the correct document ID and title; body contains the expected text |
| Unchanged plain-text `push` | Succeeds; remote text and title remain the same. This was **not** a zero-write/no-op assertion |
| One-word local edit then push | Intended remote text changes; the other document remains untouched |
| Punctuation/Unicode title and local filename | Title `Director's notes: Plan (Σ) #1` survives metadata parsing; filename with apostrophe, spaces, parentheses and accented letters works |
| Local filename changed to resemble another document | Push follows the `gdoc:` ID in frontmatter, updates the intended source, and leaves the similarly named other document alone |
| Local `title:` metadata edited | Body is pushed to the same ID; remote title stays unchanged. The local title field is not a rename instruction |
| CRLF line endings | Frontmatter and a one-word body edit parse and push correctly |
| Local filename beginning `--` | Works when supplied as an absolute path, as tested |
| Pull from a URL opening the second tab | Pull exports **both tabs** and writes document-level `gdoc`/`title` metadata, without tab binding |
| Modified local copy of two-tab document pushed | Exit 3 with the explicit two-tabs-to-one collapse warning; both tab identities, titles and sentinel texts remain unchanged |

## The tab limitation is explicit

`pull --help` and `push --help` expose no `--tab` option. A `?tab=...` URL does not make the resulting file safe for selected-tab push: the local file is bound to the document as a whole. The live pull contained headings for both `Tab 1` and `Second`, followed by each tab's text. The subsequent push was refused by the multi-tab guard—not by a transient read conflict.

That is a capability boundary, not a newly discovered overwrite failure. The user can use native tab-oriented commands for selected-tab work. No collapse override was requested or used in this test.

## Limits and reproducibility

These checks establish text, identity, title and tab-isolation outcomes for tiny plain documents. They do not certify preservation of native styles, comments, images, chips, list definitions, page setup or other rich structures during whole-document import. Broad no-change Markdown rebuild and styling losses were already part of the campaign and were deliberately not promoted again.

Every remote mutation used the explicitly verified personal identity. Local Markdown files were confined to the ignored `.local-hunt/r2-local-files` directory with owner-only permissions; resource IDs stayed in `.local-hunt/r2-local-ledger.json`. No real files were overwritten, no permissions or sharing changed, no files were deleted, and no collection was modified.

```sh
~/.local/share/uv/tools/workspace-mcp/bin/python hunt/round2/local-roundtrip.py
```

Rerunning creates three additional synthetic documents and reuses only the probe's own local files. The bounded area is complete; the evidence supports recording passing coverage and stopping here.
