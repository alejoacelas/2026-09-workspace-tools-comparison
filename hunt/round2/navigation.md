# Native navigation and public-URL image controls

15 checks on one synthetic personal Doc with Main → Branch → Leaf nesting and a Peer tab.

| Check | Result |
|---|---|
| tab_tree_depth | pass |
| all_tab_markers | pass |
| grandchild_read_by_title | pass |
| structure_full_topology | pass |
| structure_selected_subtree | pass |
| structure_supported_mask | pass |
| toc_repeated_titles_and_levels | pass |
| toc_deep_links | pass |
| toc_depth_filter | pass |
| toc_grandchild_no_links | pass |
| image_insert_explicit_dimensions | pass |
| image_insert_grandchild_width_only | pass |
| image_inventory_all_nested_tabs | pass |
| image_replace_preserves_identity_size_tab | pass |
| image_inventory_select_one | pass |

Raw resource identifiers and signed image URLs are confined to ignored local scratch. Public evidence publishes only synthetic headings, tab names, dimensions, counts and boolean comparisons. Images were inserted/replaced using already-public synthetic report PNG URLs; no local-image upload, sharing, temporary deletion or collection mutation occurred.

These are bounded positive controls, not proof all heading or image scenarios work. Replacement checks establish retained object identity/size/tab, not pixel-level center-crop fidelity.

Image insertion preserved aspect ratio: a 1120×496 PNG requested within 112×64pt became 112×49.6pt; width-only 140pt became 140×62pt. An initial harness expectation of a stretched 112×64 image was corrected against [Google’s objectSize rules](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request#InsertInlineImageRequest), rather than counting correct behavior as a bug.
