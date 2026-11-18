# Risk Tiers (generic example)

> **Generic template.** A three-tier scale for the class exercises. Your team replaces the tiers, the questions and the required controls with its own.

Give a use case the highest tier that any one question puts it in.

| Question | Low | Medium | High |
|---|---|---|---|
| What data can Claude Code reach? | Public or sample code only | Internal source code | Customer data, credentials, regulated data |
| What can it change? | A local working copy | Branches and pull requests | Shared systems, production configuration, deployments |
| Who sees the output? | Only its author | The team, after review | Customers or other systems, with no review |
| What identity does it use? | The user's own login | A team-owned service identity | A shared or long-lived key |

## Example controls by tier (replace with your own)

| Control | Low | Medium | High |
|---|---|---|---|
| Intake checklist | Required, owner signs | Required, owner and one reviewer sign | Required, plus a documented review date |
| Sandbox | Recommended | Required | Required, with `failIfUnavailable` set to true |
| Deny rules for secrets | Required | Required | Required, plus shell protection (sandbox `denyRead`) |
| Hooks that block risky commands | Optional | Required | Required, tested, with a log |
| MCP servers | Any approved server | Fixed set | Fixed set, reviewed per server |
| Human review of output | Optional | Required | Required, by a second person |
