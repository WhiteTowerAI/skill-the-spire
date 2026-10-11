# Surface: Act

Use this surface for a complete playable world chapter. An Act is not just a background: it owns
one run slot, map generation, weak/regular/elite/Boss Encounter pools, Event and Ancient pools,
treasure and Rest Site presentation, music/ambience, map colors, and an explicit route by which a
singleplayer run can enter it.

Registration and reachability are separate. `.Act<T>()` adds the model to `ModelDb`; it does not
make a run enter that Act. Every Act SPEC must also select exactly one supported entry policy.

## DESIGN and SPEC vocabulary

Settle and write:

- slot/index: first, second, or third chapter (`0`, `1`, or `2`);
- entry policy: force (one Act or a weighted candidate set), uniform pool with the existing
  chapter, or weighted pool with the existing chapter;
- eligibility, force priority, and tie behavior; for weighted entry, every candidate weight
  relative to the existing chapter's fixed weight 1;
- map length and exact Unknown/Rest counts or deterministic formulas using the supplied map RNG;
- nonempty weak, regular, elite, and Boss Encounter sets, Boss discovery order, ordinary Events,
  and Shared/Act-scoped Ancient relations;
- unlock policy: available in the selected singleplayer entry rule; new Progression/epoch/unlock
  integration is deferred;
- title in English and Simplified Chinese, map colors, music/banks/ambience, chest resource/skins/
  sound, background, combat layers, Rest Site scene, and three map textures; and
- a real act-transition SelfTest that reaches map, weak/regular/elite/Boss combat, Event, Ancient,
  chest, and Rest Site consumers without treating registration as entry proof.

All authored Act entry predicates must reject `ctx.IsMultiplayer`. Keep
`AllowInRandomActList == false`: organic vanilla random-list opt-in has no singleplayer predicate
and would create a deferred Multiplayer interaction. Use the explicit force/uniform/weighted
entry routes instead.

## Authoring route

- Read `recipes/act.md` for the `ModActTemplate` members, `.Act<T>()`, entry policies, content
  relations, deterministic RNG, localization, and assets.
- Read `recipes/monster.md` and `recipes/event.md` for custom Encounter and ordinary Event nodes,
  and `recipes/ancient.md` for new Ancient nodes.
- Read `reference/lifecycle-state-rng.md` for lifecycle and supplied-RNG rules. Do not use
  `System.Random`, process-local randomness, a Progression route, or a Multiplayer route.

## Proof matrix

Use a fresh singleplayer run and the real transition into the selected slot:

1. assert the canonical Act is registered once but the mutable run Act occupies only its selected
   slot after the declared force/pool rule resolves;
2. drive eligible and ineligible contexts and, for force rules, priority/tie behavior; for uniform
   or weighted pools, inject deterministic supplied RNG and assert the selected candidate without
   claiming a statistical distribution from samples;
3. assert the generated map has the declared floor and point counts and every runtime-required
   Encounter/Ancient pool is nonempty;
4. enter representative weak, regular, elite, Boss, ordinary Event, Ancient, chest, and Rest Site
   nodes and assert their exact registered identities and post-state;
5. save/load in the Act and assert the same mutable Act identity, room state, and no duplicate
   registration or re-roll; and
6. headed review checks map/background layering, path colors, chest, Rest Site, music/ambience,
   and mouse/controller navigation.

Compile and model lookup establish neither Act entry nor usable rooms/assets. Until this matrix
runs, new Act behavior and all presentation remain game-unobserved.
