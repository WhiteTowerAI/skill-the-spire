# Design - preserve the human decision

Write `DESIGN.md` after the material choices are settled. This is a short human-readable
record, not a schema and not a proof.

`DESIGN.md` owns only:

- the intended player experience;
- decisions the user accepted, including important trade-offs and deliberate departures;
- the current scope to implement;
- explicit placeholders, deferred ideas, unsupported gaps, and out-of-scope work; and
- open tuning hypotheses that must not be reported as measured or playtested.

Use the depth the request needs. A complete exact Card can be four short sections. A Character
or interacting content set may need rationale, relationships, formulas, and tuning notes. Do
not add IDs, JSON blocks, ledgers, identity-anchor tables, experience settlements, impact
queues, or a formal completeness claim.

Recommended shape:

```markdown
# DESIGN - <working title>

## Intent
<what the player should do, notice, or feel>

## Decisions
- <accepted behavior, value, theme, or trade-off>
- Output player-facing text in English and Simplified Chinese.

## Current Scope
- <what this build includes>

## Not Now
- <placeholder, deferred idea, unsupported boundary, or explicit exclusion>

## Open Hypotheses
- <only unmeasured balance or experience assumptions; omit when none>
```

For a revision, edit only affected decisions and scope. Keep rejected alternatives only when
they prevent a later agent from reintroducing them. If no maintained route exists but a public
implementation can be grounded, record it as a Mod-local public-API implementation and continue
to SPEC. Stop only when public grounding fails or the implementation requires prohibited
techniques.

Existing projects may keep old DESIGN metadata. Read the human meaning, ignore the old blocks,
and do not rewrite an unchanged project merely to match this format. A project with SPEC but no
DESIGN may resume from its existing artifacts; create a compact DESIGN only when the user asks
for a design change or the current intent cannot otherwise be recovered.

After DESIGN, write `SPEC.md`. Confirm the implementation in one concise message before
scaffolding when the request involved material inferred choices; exact zero-question fast-path
work may continue directly.
