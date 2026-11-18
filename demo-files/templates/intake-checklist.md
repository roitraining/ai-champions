# Claude Code Use Case Intake Checklist

> **Generic template.** This is a starting point from ROI Training. Your team replaces the questions, the answers and the tier rules with its own. Nothing here is a policy until your team adopts it.

Use one copy per use case. Answer every section. "Unknown" is a valid answer, and it is a finding.

**Use case name:** ______________________  **Date:** __________  **Completed by:** ______________________

## 1. Purpose and owner

- What job does Claude Code do in this use case, in one sentence?
- Who is the named owner (a person, not a team alias)?
- Who is the backup owner?
- Who decides to approve, change or stop this use case?

## 2. Data

- What data can Claude Code read in this use case (source code, tickets, logs, customer data, credentials)?
- What is the most sensitive item it could reach by accident?
- Is any regulated or personal data in reach? If yes, where does it live and who approved access?
- Can data leave the machine (network calls, pasted output, commits)?

## 3. Repositories

- Which repositories are in scope? Which are explicitly out of scope?
- Can Claude Code push, open a pull request, or only commit locally?
- Which branches are protected, and does the protection hold for Claude Code's changes too?

## 4. Tools and servers

- Which built-in tools are needed (file edit, shell, web)? Which are not?
- Which MCP servers are needed? Who approved each one, and as what identity does each one authenticate?
- Which plugins are installed, from which source, and who reviewed them?

## 5. Model and effort

- Which model and effort level is the default for this use case, and why?
- When may a user switch up or down?
- Who pays attention to cost and speed?

## 6. Permissions and sandbox

- Which actions run without asking, which ask, and which are denied?
- Is the sandbox required? If it cannot start, should Claude Code refuse to run?
- Which files are protected from reading and writing?

## 7. Credentials

- Whose identity does Claude Code use (a person's own login, a service account, a shared key)?
- Where is each credential stored, who owns it, how long does it live, and how is it rotated?
- What happens to it when its owner leaves the team?

## 8. Review and escalation

- Who reviews the output before it is merged or shipped?
- What must a human always approve?
- Who is called when something goes wrong, and how quickly?

## 9. Logging

- What is logged (tool calls, blocked actions, sessions)? Where does the log live and who can read it?
- Which rule can you prove from the log today? Which rule cannot be proved yet?
- How long is the log kept?

## 10. Exit criteria

- What would make this use case stop (an incident, a failed review, a missed control)?
- What evidence is needed to move it to a higher or lower risk tier?
- When is the next review of this intake?

## Risk tier (record the result)

Tier: [ ] Low  [ ] Medium  [ ] High  (use `risk-tiers.md`, or your own scale)

Reason in one or two sentences:

Sign-off (owner): ______________________  Date: __________
