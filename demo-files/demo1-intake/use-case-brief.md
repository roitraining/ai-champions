# Use Case Brief: Release Notes Assistant (fictional)

A fictional engineering team, Meridian Freight Systems, wants Claude Code to help with a weekly job. Use this brief to fill in `templates/intake-checklist.md` in Demo 1.

**What the team wants.** Each Friday, an engineer opens the `tally-api` repository, asks Claude Code to read the git log since the last tag, draft release notes into `RELEASE_NOTES.md`, and open a pull request for the notes.

**Who.** The owner is the engineering manager, Dana Okafor. The backup is the tech lead, Ravi Menon. Six engineers will use it.

**Data.** The repository holds application source code and a `config/` folder. The `config/` folder has a `staging.env` file with a staging database password (a real password for the staging system). Commit messages sometimes quote customer ticket numbers. No customer data is in the repository.

**Repositories.** Only `tally-api`. The team also has `billing-core` and does not want Claude Code anywhere near it.

**Tools.** Claude Code's file tools and the shell. The team would like to add a ticket-system MCP server later so notes can link tickets. The server would sign in with a shared service account.

**Model.** Whatever the account default is. Nobody has thought about effort level.

**Permissions.** Today every engineer clicks "allow" on prompts. Nobody has set deny rules. Claude Code can run `git push`.

**Credentials.** Engineers sign in with their own seats. One engineer keeps a personal key in a `.env` file in the repository folder for a side script.

**Review.** The pull request is reviewed by one other engineer. Nothing is logged except what git records.

**Exit.** The team has not discussed what would stop the project.

## Task for the room

1. Fill in all ten sections from this brief. Write "Unknown" where the brief is silent.
2. Give the use case a tier using `templates/risk-tiers.md`.
3. Name the one answer that decided the tier.
