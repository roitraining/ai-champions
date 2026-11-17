# Harbor Example Co: Claude Code credential audit sample

Fictional. Every secret in this tree is a placeholder (`FAKE-KEY-DO-NOT-USE-NNNN`, `FAKE-TOKEN-DO-NOT-USE`). Report the pattern, not the value.

Layout:

- `org/` holds a managed settings file and three inventories: credentials, CI secrets and departures. The audit date is 2026-10-12.
- `repos/billing-service`, `repos/inventory-service`, `repos/payments-gateway` each hold a `.claude/` folder and a CI workflow. Two of them also hold a `.env` file or a key helper.

Harbor's credential policy, for reference while you audit:

- Every credential has a named owner. A credential owned by an individual is re-issued to
  a team when that person changes role or leaves.
- Every credential is rotated **at least every 180 days**, and on the day an owner leaves.
  A credential whose `last_rotated` is `never` is measured from its `created` date.
- CI secrets are scoped to a single repository.

Your task and the findings layout are in `labs/lab-5-credential-audit-take-home.md`. Use `../findings-template.md`.
