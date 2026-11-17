# Lab 6: Context Engineering (take-home)

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Labs](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Measure what loads into the context window at startup, trim a `CLAUDE.md` and a plugin's descriptions, measure again, and write two rules for your team. Time: take-home, no set time.

**Files:** `$FILES/lab6-context`: `shopkit/` (a sample project with a bloated `CLAUDE.md`), `shopkit-plugin/` (a plugin with long descriptions), `original/` (the untouched `CLAUDE.md` the checker measures your trimmed one against) and `original-plugin/` (an untouched copy of the plugin, so you can compare descriptions before and after and restore one you cut too far), `measure.csv`, `RULES-LEARNED.md`, `check_lab6.py`.

**Context:** At startup, before you type anything, `CLAUDE.md`, auto memory, MCP tool names and skill descriptions are already in the context window, and each file Claude reads adds to it. `/context` shows a live breakdown by category with suggestions, including which `CLAUDE.md` and memory files loaded. `/memory` opens and edits them. `/compact` replaces the conversation with a summary, and `/clear` starts fresh. Every enabled plugin puts the names and descriptions of its commands, skills and agents in the context window on every turn, and `claude plugin details <name>` prints a projected token cost. A shorter description can stop a command being chosen, so test it after you shorten it. This lab does not quote any size, threshold or limit. For how `CLAUDE.md` files are found and loaded, read the memory documentation (https://code.claude.com/docs/en/memory). For model and context options, read the model configuration documentation (https://code.claude.com/docs/en/model-config). For what fills the window, see https://code.claude.com/docs/en/context-window.

**Steps:**

1. **Measure before (about 10 minutes).** Goal: three numbers recorded.
   - In `$FILES/lab6-context/shopkit`, start `claude` and run `/context`. Record the startup total and the `CLAUDE.md` line in `measure.csv` as the tool shows them (tokens or percent). The default `/context` view shows `Memory files: 1 file, 1.3k tokens` and does not name `CLAUDE.md`; run `/context all` to see it by name, and record tokens, because the percentage may not move (3% before and after on the class image). Then run `claude --plugin-dir ../shopkit-plugin plugin details shopkit-helpers` and record the projected token cost.
   - Hints: copy the numbers exactly as displayed and do not convert them. Fill the six rows that ship in `measure.csv`; you may add rows of your own below them, but an added row does not stand in for a shipped row you left blank.

2. **Trim `CLAUDE.md` (about 20 minutes).** Goal: a `CLAUDE.md` at least 40 percent shorter that keeps what Claude needs.
   - Acceptance criteria: the five facts that matter survive (the test command, never committing `.env`, integer cents for money, the public API path, and the indentation rule); stale and duplicated instructions are gone; no motivational text remains.
   - Hints: for each line, ask whether Claude would behave differently without it. Two of the instructions contradict each other, and some describe a tool that no longer exists. A rule that must persist belongs in the project-root `CLAUDE.md`. When two instructions contradict each other, keep the one that is still true: the checker reads a line as still prescribing the old tool when the old tool is what it tells Claude to run, so "run the tests with `nosetests`, not `python3 -m pytest -q`" fails the stale row and does not count as keeping the test command either. Deleting the stale line is enough; naming it in order to retire it ("use `pytest`, not `nosetests`"; "Python 2 support was dropped") also passes.

3. **Trim the plugin (about 15 minutes).** Goal: every command and agent description is short and still says when to use it.
   - Acceptance criteria: each description is 200 characters or fewer (a lab rule of thumb and not a product limit), at least 40 characters, and still names its topic (price, stock, refund, cart).
   - Hints: lead with the job and the trigger, and cut the filler. Test that the commands are still chosen: ask a matching question and an unrelated one in a session with the plugin loaded.

4. **Measure after (about 10 minutes).** Goal: the same three numbers again.
   - Restart `claude`, run `/context`, and run `plugin details` again. Record all three in `measure.csv`.
   - Hints: use the same session setup as in step 1 so that the comparison is fair.

5. **Write two rules (about 10 minutes).** Goal: two rules for your own team in `RULES-LEARNED.md`.
   - Acceptance criteria: exactly two numbered rules, each starting with a verb and ending with a "because" clause that points at something you measured.
   - Hints: `1.` or `1)` both count, and a rule may wrap onto an indented second line. Put evidence or notes under a heading below the two rules, and write them as prose or `-` bullets: the checker reads any numbered line with a "because" clause as a rule, wherever in the file it sits.

6. **Check it.** From `$FILES/lab6-context`, run `python3 check_lab6.py`.

**Checkpoint:** The checker reports at least 85, and `measure.csv` shows a lower number after than before for at least two of the three measurements.

**Common problems:**

- You cut the facts that matter: the checker names the missing ones, and each one is worth 3 of the 15 points. Wording is yours: the checker accepts any phrasing that keeps the fact.
- The numbers did not change: compare like with like. `/context` also counts other files that loaded.
- A description is shorter and the command stopped being chosen: add the trigger back in fewer words.
- You kept the contradiction and picked the wrong side: a line that tells Claude to run `nosetests` instead of `pytest` scores zero on both the stale row and the test-command fact. Keep the instruction that is still true.
- `measure.csv` reports a row as blank although you filled in six values: the checker matches the six rows it shipped (a `/context` total, a `CLAUDE.md` line and a plugin token cost, before and after), and names the one still missing. Extra rows of your own are fine but do not replace one of the six.
- A third numbered line is read as a third rule: it has a "because" in it. Turn evidence notes into `-` bullets or prose.
- You wrote rules with no measurement behind them: change the because clause to what you saw.
- You quote a number from memory in your rules: remove it, or link to the documentation.

**Scoring rubric (100 points, from `check_lab6.py`):**

| Item | Points |
|---|---|
| `CLAUDE.md` at least 40 percent shorter | 15 |
| The five facts that matter are still there | 15 |
| No stale instruction remains | 10 |
| Every description 200 characters or fewer | 12 |
| No description shortened to nothing | 6 |
| Every description still names its topic | 12 |
| `measure.csv` complete | 15 |
| Two rules, each with a because clause | 15 |

An untouched project scores about a third of the points. The five-facts row gives 3 points per fact, so one missing fact costs 3 and not 15; every other row is all or nothing. The checker cannot read `/context` output, so the measurement rows are self-reported, and the facilitator may ask to see a screen.
