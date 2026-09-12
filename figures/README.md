# Before / Expected / Observed figures

These are reconstructed illustrations, not screenshots. The first three depict synthetic live results; the escaped-pipe figure depicts executed offline parser output. The renderer follows the campaign-private visual standard: one case per figure, consistent Arial scale/alignment, blue/green/red state labels, content-sized panels, and diagnostics outside document text.

- `gdoc-bold-loss.png`: ordinary replacement removes unrelated bold; native-state evidence in `../evidence/live-benchmark.json`.
- `gdoc-unicode-search.png`: `İ cat` becomes `İ cdog`; same live evidence.
- `shared-nested-list.png`: both native writers flatten the child; evidence in `../evidence/live-feature-checks.json`, with a successful independent reference in `../evidence/live-list-oracle.json`.

An independent agent inspected the actual PNGs against the campaign standard and a native reference. The final list figure leaves the blank Before specimen empty, uses a hollow child marker in Expected, and attributes the observed failure to both tools. Commands, setup and evidence limits appear beside each figure in the main report.

Regenerate with `uv run --with pillow python figures/render.py`. Fonts use macOS Arial paths; substitute equivalent Arial font files on another OS. No private campaign case data is copied into these figures.

- `gdoc-escaped-table-pipe.png`: expected key/value `A|B` / `100` versus parsed `A` plus backslash / `B`; generated directly from the corpus evidence. Independently reviewed for accurate cells, consistent scale and explicit offline-only labeling.
