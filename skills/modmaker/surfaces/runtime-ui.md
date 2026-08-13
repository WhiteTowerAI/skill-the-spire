# Surface: Runtime UI

Use this surface for one Mod-owned player workflow assembled from a top-bar entry point, short
notifications, runtime hotkeys, a capstone screen or floating window, a searchable catalog, and
fixed public Godot node attachments. Runtime UI owns the workflow's local interaction, node and
handle lifetimes, localization, refresh, focus, close behavior, and headed proof.

This surface does not own Card Piles, content-model presentation, or any deferred product family.
Do not add a Settings page or binding, Progression or post-run Badge view, Telemetry consent,
Update Check prompt, Multiplayer control/synchronization, or an integration to those families.

## DESIGN and SPEC vocabulary

Settle and write only the controls selected by the accepted workflow:

- stable workflow/button/hotkey/provider/attachment IDs, owning coordinator node, creation time,
  cleanup time, and behavior before a player or UI host exists;
- top-bar icon/fallback, order/offset, bilingual hover tip, click outcome, visibility, selected/open
  state, and optional count; every per-frame provider must be fast, pure, and null-player safe;
- Toast level, body/title/image, duration or persistence, click/dismiss action, progress, tracked
  updates, terminal close, and what happens when no host is ready;
- runtime hotkey binding(s), semantic action, text-input/dev-console suppression, input handling,
  optional Steam Input action exposure, rebind policy, and disposal owner;
- capstone screen content, local focus/backstop/close behavior, replacement by another capstone,
  and `NetScreenType.None`; no remote-screen synchronization is authored;
- floating-window title/content, fixed or movable/resizable behavior, min/initial/max geometry,
  viewport constraint, ownership of detached/replaced content, and close/cleanup policy;
- catalog list/grid and inline/drawer detail mode, stable unique items, filters, localized search/
  empty/detail text, selection, quick actions, refresh, and controller focus;
- optional search-expansion provider ID, supported locale/text, deterministic bounded alternate
  forms, local-data invalidation, and disposal; and
- node attachment's exact stable public parent type, factory/scene source, name/order, derived-type
  policy, duplicate policy, add/setup timing, insertion point, lookup, and parent-tree cleanup.

If the workflow uses shell tokens, namespace them under the Mod and let only the Mod's UI consume
them. Respond to the published snapshot through `OnApply`; never change the active global theme or
style unrelated game/framework controls as product behavior.

## Authoring route

- Read `recipes/runtime-ui.md` and `reference/lifecycle-state-rng.md`.
- Read `reference/build-constraints.md` for packaged icons, `.tscn` scenes, C# script registration,
  and bilingual localization.
- Register top-bar definitions before the current `NTopBar` becomes ready. Retain and dispose every
  hotkey and search-provider handle from the coordinator that owns the workflow.
- Create and mutate Catalog, Window, Capstone, Toast, and Godot nodes only on the Godot main thread.
  Keep search expansion callbacks deterministic, thread-safe, non-blocking, and free of file or
  network I/O.
- Attach only to an exact public stable host documented by the recipe. Do not use Node Attachment as
  a generic patching escape hatch or target an internal/private node.

## Proof matrix

1. Assert stable owned IDs, one registration/attachment per declared owner, duplicate policy, and
   correct behavior before/after host and local-player availability.
2. Drive the real top-bar button and hotkey through mouse, keyboard, and controller as applicable;
   assert open/selected/count/visibility state, suppression, handled-input behavior, and disposal.
3. Drive transient and tracked Toasts; assert exact click/update/progress/duration/close state and
   that no stale Toast or callback survives its owner.
4. Open/toggle/replace/close the real local capstone and floating window; assert focus, backstop,
   content ownership, geometry bounds, viewport resizing, and cleanup.
5. Populate the real Catalog with boundary and ordinary data; assert unique IDs, search, every
   filter, stable selection across refresh, details, quick actions, empty state, and the 16,384-item
   and 512-character limits where relevant. Filters must be fixed before the control enters the
   scene tree.
6. Exercise every search-provider locale and invalidation/disposal case, including concurrent
   calls, unsupported input, duplicate/over-limit expansions, and absence of network/file work.
7. Headed review covers real layout at selected aspect ratios, icon/text readability, mouse and
   controller focus/navigation, window drag/resize/constraint, Toast timing/animation, and visual
   response to the active shell-theme snapshot.

Compilation, direct callback invocation, registry lookup, or a constructed Godot node is not UI or
input observation. This M8.8 Runtime UI route remains game-unobserved until its real hosts run.
