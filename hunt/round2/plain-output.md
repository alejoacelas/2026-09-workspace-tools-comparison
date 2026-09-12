# Plain output escaping: title scope of H18

Live checks against pinned gdoc `dbfa4c34bfa699ee8dd9839da85eea1fac177d44`: **two output failures, two passing controls, one unconfirmed fixture**. These extend H18's delimiter-escaping family; they are not additional distinct bugs.

| Case | Native fixture | Plain output | JSON control |
|---|---|---|---|
| Scoped `ls`, ordinary title | `Café Σ budget` | Pass | Pass |
| `tabs`, ordinary title | `Tab 1` | Pass | Pass |
| Scoped `ls`, tab/newline in title | Exact requested title verified in Drive | Fails record/field roundtrip | Exact title preserved |
| `info`, tab/newline in title | Exact requested title verified in Drive | Fails record/field roundtrip | Exact title preserved |
| `tabs`, tab/newline in title | Native update returned HTTP 500; reread remained `Tab 1` | Unconfirmed | Not tested |

The accepted document title is `Budget\tQ4\nBoard`, where `\t` and `\n` represent literal tab and newline characters. `ls --plain` emits it without quoting: the document becomes two logical rows, with the first row's name truncated to `Budget` and its MIME-type field replaced by `Q4`. `info --plain` similarly emits a three-field title row followed by a one-field `Board` row. Both commands exit 0.

Validation uses Python's quoting-aware `csv.reader` with a tab delimiter, double-quote quote character, and strict parsing. It checks the expected field counts, logical record count where applicable, and exact title. This is not a failure caused merely by splitting on newline. JSON preserves the native title in both cases and is the usable workaround.

The tab-title setup failed in Google's API before gdoc was tested; it provides no evidence of a gdoc `tabs` escaping defect. The probe records this limitation rather than treating backend setup failure as an application failure.

Only previously created synthetic fixtures were used. Listing was scoped to their dedicated parent folder. Public output replaces file/tab IDs and owner details; raw responses remain in the private local directory. See [machine-readable results](plain-output.json) and [reproduction script](plain-output.py).
