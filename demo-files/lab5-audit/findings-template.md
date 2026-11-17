# Credential Audit: Findings

> **Three things this template assumes, so everyone uses the words the same way.**
>
> - **File and line** may list more than one location when a finding genuinely spans
>   files. A secret shared across repositories lives in the inventory row *and* in each
>   workflow that uses it. Keep it as one finding with several locations.
> - **Severity** — high: the credential is already exposed, or is live and unaccountable.
>   Medium: exposure is possible but needs something further to happen, and nothing shows
>   it has. Low: hygiene that does not expose a credential on its own.
> - **Owner** — if a credential you found is not in the inventory and has no owner, write
>   `unassigned - not in the inventory` and say who should own it. A credential nobody
>   tracks is a finding about the inventory, not a gap in your report.
>
> Keep the headings (`## Finding 1`) and the bold field labels as they are below. The
> format checker reads them to find your answers.


Audit target: `harbor-org` (fictional sample). Auditor: ____________  Date: ____________

Write one block per finding. A finding is a real credential or secret hygiene problem. Do not list a clean item as a finding.

## Finding 1

- **File and line:**
- **What is wrong:**
- **Risk:**
- **Severity:** high, medium, or low
- **Fix:**
- **Rotation step:**
- **Owner:**

## Finding 2

- **File and line:**
- **What is wrong:**
- **Risk:**
- **Severity:**
- **Fix:**
- **Rotation step:**
- **Owner:**

(Copy the block for each further finding.)

## Not a finding

List items you checked and found sound, with one line on why.

-

## Priority order

Rank the findings and give a reason for each position.

1.

## Rotation and ownership plan

For every credential in the inventory: the owner, how long it lives, where it is used, how it is rotated, and what happens when its owner leaves.

| Credential | Owner | Lifetime | Where used | Rotation | If the owner leaves |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Credential options for automation

One paragraph (lab step 5). Compare a personal token, a shared key and a federated or
service identity: one strength and one weakness each, then say which you would use for
automation and why. Mark anything you could not confirm from the course materials as
`unconfirmed`. The format checker does not score this section; your facilitator reads it.
