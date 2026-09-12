# Nested lists: native outcome overrides request-intent checks

**Both tools flattened the two-space child in the live fixture.** The offline corpus's gdoc “pass” means its emitted requests contain the expected leading tab; it does not prove Google's resulting list nesting. This is a limitation of the observer, not evidence against the live result.

The existing corpus already uses `- Parent\n  - Child\n- Sibling` with **two** spaces; the live fixture changes only the final item's text to `Peer`. There was no two-versus-four-space mismatch explaining the discrepancy.

| Input child indentation | gdoc parser | Complete gdoc `write --tab` helper | Workspace converter | Live Google outcome |
|---|---|---|---|---|
| Two spaces | Inserts one leading tab before Child | Tab survives into the sent batch | No nesting tabs | Both child paragraphs have 18pt first-line/36pt start indentation and no nonzero nestingLevel |
| Four spaces | Inserts two leading tabs before Child | Both tabs survive into the sent batch | No nesting tabs in the converter's list emission | Not tested live in this cross-check |

The four-space interpretation is an explicit gdoc parser convention: `_list_level` uses `columns // 2`, and upstream `test_four_space_indent_is_two_levels` asserts it. It should not be assumed equivalent to every CommonMark list parser.

I intercepted the complete `insert_markdown_into_tab` helper with a mocked blank document and mocked Google service. For both indent widths, the helper submitted exactly one revision-pinned batch. `_strip_trailing_newline_unless_hr` removes only the final newline; the child tabs remain. There is **no later cleanup batch** for these table-free inputs, so an additional local cleanup phase does not explain the flattened live output.

A later [direct Google reference](live-followups.json), `native_grouped_bullets`, used one grouped bullet request and produced child `nestingLevel: 1`, 54pt first-line indent and 72pt start indent, versus parent/peer 18pt and 36pt. Google therefore supports the intended structure, and agreement between the two tool outputs would have accepted a shared failure.

The precise cause inside gdoc's request sequence is not established here. gdoc sends separate `createParagraphBullets` requests in document order. The offline observer models leading-tab removal but not Google's complete list joining, paragraph range interpretation, or subsequent bullet updates. Do not report that gdoc supports correct live nesting based only on its parser or request tests.

- [Reproducer](../probes/nested-list-crosscheck.py): run `repos/gdoc/.venv/bin/python probes/nested-list-crosscheck.py`.
- [Captured complete request bodies](nested-list-crosscheck.json).
- [Live native snapshots](live-feature-checks.json), `case=nested_lists`.
- [gdoc nesting implementation and parser tests](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/mdparse.py#L249), [test convention](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/tests/test_mdparse.py#L744), [complete tab helper](https://github.com/LucaDeLeo/gdoc/blob/dbfa4c34bfa699ee8dd9839da85eea1fac177d44/gdoc/api/docs.py#L1411).


The later [controlled native replay](live-list-oracle.json) held gdoc's text/style requests fixed: per-item bullet requests flattened the list; one grouped request restored nesting. This establishes grouping as a useful fix direction without applying an upstream patch.
