# Repair - fix the observed failure

Repair starts from the real compiler output, build diagnostic, fresh host log, or failed
structured state assertion. Do not infer success from an exit code and do not rerun a changed
Mod without rebuilding it.

## Decide what must change

- A compiler, resource, manifest, localization, packaging, or deployment failure is repaired at
  the earliest source/build layer that produced it.
- A structured Tier 2 mismatch is repaired in the implementation. The expected value comes
  from SPEC, never from the observed run: change a SelfTest expectation only when it encoded
  SPEC wrongly (for example it left out a native modifier the SPEC's result includes), and
  record that reason in `MEMORY.md`. Never set an expectation to the observed value to make
  the check pass.
- If the code does not implement the accepted SPEC, correct the code or SPEC detail without
  changing the intended result.
- If the fix would change player-visible behavior, text, scope, or presentation, stop and obtain
  acceptance; update DESIGN and SPEC before code.
- If a maintained route is absent, or runtime evidence contradicts it, implement the operation
  as a Mod-local route under `../sts2api/grounding.md` § Mod-local Routes and record
  the contradicted route in `MEMORY.md` as a pack defect. Never approximate it with ungrounded
  symbols or patches.

## Bounded loop

1. Capture the exact failure signature and current stage in `MEMORY.md`.
2. Read the matching section of `../sts2api/errors.md`, or form one narrow hypothesis
   from the actual failing layer when no entry matches.
3. Make one focused fix.
4. Re-run the earliest meaningful check: preflight for a route/reachability change, Build for
   source or resource changes, Tier 1 for load/registration, and Tier 2 for behavior.
5. Record the result. Stop after three unsuccessful fixes at the same stage.

On success, update the simple `PLAN.md` checklist and continue. On exhaustion, leave the stage
unchecked and report the attempts, exact remaining signature, and best grounded next step. A
confirmed reusable diagnostic may be recorded in project `MEMORY.md` as an `errors.md` candidate;
never edit an installed skill payload from a generated Mod project.
