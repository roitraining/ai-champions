# Lab 6: Context Engineering (take-home)

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** Take-home, no set time

> Part of **[AI Champions Training: Labs](README.md)**.

## What you will do

At startup, before you type anything, Claude Code has already loaded `CLAUDE.md`, auto memory, MCP tool names and skill descriptions into the context window. Every file Claude reads adds to it. Every enabled plugin adds the names and descriptions of its commands, skills and agents on every turn.

You measure that load, trim a `CLAUDE.md` and a plugin's descriptions, measure again, and write two rules for your team.

| You measure | With |
|---|---|
| The startup total | `/context all` in a Claude Code session |
| The `CLAUDE.md` line | `/context all` |
| The plugin's projected token cost | `claude plugin details shopkit-helpers` |

Commands you use:

- `/context` shows a live breakdown of the context window by category.
- `/memory` opens and edits the memory files.
- `/compact` replaces the conversation with a summary. `/clear` starts fresh.
- `claude plugin details <name>` prints a projected token cost.

This lab does not quote any size, threshold or limit. Read the documentation for those: [how `CLAUDE.md` files load](https://code.claude.com/docs/en/memory), [model and context options](https://code.claude.com/docs/en/model-config), and [what fills the window](https://code.claude.com/docs/en/context-window).

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md)
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Copy the lab folder and run the checker once

Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/work && cp -r $FILES/lab6-context ~/work/lab6-context && cd ~/work/lab6-context && ls
```

**Expected output** (the order may differ):

```
RULES-LEARNED.md  check_lab6.py  measure.csv  original  original-plugin  shopkit  shopkit-plugin
```

What each item is:

- **`shopkit/`** is the sample project. You trim its `CLAUDE.md` in place.
- **`shopkit-plugin/`** is a plugin with long descriptions. You trim them in place.
- **`original/`** and **`original-plugin/`** are untouched copies. The checker measures your `CLAUDE.md` against `original/`. Do not edit them.
- **`measure.csv`** and **`RULES-LEARNED.md`** are the two files you fill in.
- **`check_lab6.py`** scores your work. It takes no arguments and reads the folder it sits in, so run it from `~/work/lab6-context`.

Count the words in `CLAUDE.md`:

```bash
wc -w original/CLAUDE.md shopkit/CLAUDE.md
```

**Expected output:**

```
 652 original/CLAUDE.md
 652 shopkit/CLAUDE.md
1304 total
```

Run the checker to see where you start:

```bash
python3 check_lab6.py
```

**Expected output:**

```
LAB 6 SCORE (local checks)
[FAIL]  0/15 CLAUDE.md is at least 40 percent shorter (652 to 652 words, 0 percent)  -> cut more of what Claude would not act on
[PASS] 15/15 The facts that must survive are still in CLAUDE.md
[FAIL]  0/10 No stale instruction remains  -> still prescribes: nosetests, Jenkins, the FTP uploader, Python 2 - delete the line, or say plainly that it no longer applies
[FAIL]  0/12 Every description is 200 characters or fewer  -> cart-reviewer=410; price-check=522; refund-policy=411; stock-report=452
[PASS]  6/6  No description is shortened to nothing (40+ characters)
[PASS] 12/12 Every description still names its trigger topic
[FAIL]  0/15 measure.csv has a value in all six rows  -> 0 of the 6 template rows have a value; still blank: the /context startup total (before); the /context CLAUDE.md line (before); the plugin details token cost (before) ...
[FAIL]  0/15 RULES-LEARNED.md has exactly two numbered rules, each with a because clause  -> found 0 numbered rule(s) in the rules list; write exactly two

TOTAL: 33 / 100
```

An untouched project scores 33. You raise it in the next steps.

> **`No such file or directory`?** `$FILES` is empty. Set it with the tip in Prerequisites and run the command again.
>
> **`python3: can't open file`?** You are not in `~/work/lab6-context`. Run `cd ~/work/lab6-context`.

---

## Step 2: Measure before

Record three numbers before you change anything.

**First, the startup total and the `CLAUDE.md` line.** Start Claude Code in the project folder:

```bash
cd ~/work/lab6-context/shopkit
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**. If no question appears, the folder is already trusted. The bottom of the screen shows `auto mode on`. Leave it.

Type:

```
/context all
```

The output is long: it lists every skill with its token cost. The first lines, which hold the totals, can scroll off the top of a small terminal window. Double-click the window's title bar to enlarge it, then run `/context all` again.

Read the output. Find the startup total and the line for `CLAUDE.md`. Write both down as the tool shows them, in tokens, with no conversion. The default `/context` view shows a line like `Memory files: 1 file, 1.3k tokens` and does not name `CLAUDE.md`. `/context all` shows it by name.

Type `/exit` and press Enter.

**Second, the plugin's token cost.** Still in `shopkit`, run:

```bash
claude --plugin-dir ../shopkit-plugin plugin details shopkit-helpers
```

**Expected output** (the last part of it):

```
Projected token cost
  Always-on:   ~597 tok   added to every session

Per-component (rounded)
  component      always-on  on-invoke
  cart-reviewer       ~130        ~50
  price-check         ~170        ~70
  refund-policy       ~140        ~40
  stock-report        ~150        ~50
```

Find the `Always-on:` line. Write down its figure, here `~597`. Your numbers may differ by a few tokens.

**Third, record all three in `measure.csv`.** Go back to the lab folder and print the file:

```bash
cd ~/work/lab6-context
cat measure.csv
```

**Expected output:**

```
step,what_to_record,value,notes
1_before,/context total for the session at startup in shopkit (as shown),,
1_before,/context line for CLAUDE.md (as shown),,
1_before,claude plugin details shopkit-helpers: projected token cost,,
2_after,/context total at startup after trimming CLAUDE.md,,
2_after,/context line for CLAUDE.md after trimming,,
2_after,claude plugin details shopkit-helpers: projected token cost after trimming descriptions,,
```

Open it in an editor:

```bash
nano measure.csv
```

Use the arrow keys to move to the first `1_before` row. The `value` field is between the last two commas of the line. Press **End** to jump to the end of the line, press **Left** once, and type the number. Fill the three `1_before` rows now. Leave the three `2_after` rows for Step 5. **Ctrl+O**, then **Enter**, saves. **Ctrl+X** exits. To use a graphical editor, open the file in **Visual Studio Code** from the desktop.

Copy the numbers exactly as displayed. If a value contains a comma, wrap it in double quotes. The checker needs a value in each of the six rows it shipped. You may add rows of your own below them, but an added row does not stand in for a shipped row.

> **The percentage did not change between runs?** Record tokens, not percent. The percentage may not move: it showed 3% before and after on the class image.
>
> **`/context` does not show a `CLAUDE.md` line?** Type `/context all`. The default view groups memory files without naming them.
>
> **`plugin details` prints an error?** Run it from `~/work/lab6-context/shopkit`. The path `../shopkit-plugin` is relative to that folder.

---

## Step 3: Trim `CLAUDE.md`

Read the file with line numbers:

```bash
cat -n shopkit/CLAUDE.md
```

`CLAUDE.md` loads into the context window at the start of every session. A line is worth keeping only if Claude would behave differently without it.

**Your task:** trim `shopkit/CLAUDE.md` in place, so that:

- it is at least 40 percent shorter. The original has 652 words, so you need **391 or fewer**
- the five facts that matter survive: the test command, never committing `.env`, integer cents for money, the public API path, and the indentation rule
- stale and duplicated instructions are gone
- no motivational text remains

Two of the instructions contradict each other, and some describe a tool that no longer exists. Keep the one that is still true. Deleting a stale line is enough. Naming it only to retire it ("use `pytest`, not `nosetests`", "Python 2 support was dropped") also passes.

> A line that tells Claude to run the old tool counts as still prescribing it. "Run the tests with `nosetests`, not `python3 -m pytest -q`" fails the stale row and does not count as keeping the test command.

Open the file:

```bash
nano shopkit/CLAUDE.md
```

**Ctrl+K** cuts the line the cursor is on. Press it once per line to delete lines. Type to edit a line.

Try it yourself first. If you get stuck, open a block below.

<details>
<summary>Show a trimmed CLAUDE.md</summary>

This version has 65 words. Replace the whole file with:

```
# shopkit

A small Python library that prices carts for a fictional store.

- Run the tests with `python3 -m pytest -q` before finishing a change.
- Never commit `.env` (it holds a database password).
- Money is integer cents, never floats.
- The public API is `src/shop/api.py`. Ask before renaming its functions.
- Use 4 spaces for indentation and keep lines under 100 characters.
```

To make the replacement in `nano`, hold **Ctrl+K** until the file is empty, then type the text.

</details>

<details>
<summary>Show a prompt you can give Claude</summary>

Start Claude Code in `~/work/lab6-context/shopkit` and type:

```
Trim CLAUDE.md to under 391 words. Keep the test command, never committing .env, money as integer cents, the public API path, and the 4-space indentation rule. Remove stale instructions, duplicates and motivational text. Where two instructions contradict each other, keep the one that is still true.
```

Then run `wc -w CLAUDE.md` yourself. Claude's own count is not your evidence.

</details>

Check the word count and the score:

```bash
cd ~/work/lab6-context
wc -w shopkit/CLAUDE.md
python3 check_lab6.py | tail -2
```

**Expected output** with the file from the first reveal:

```
65 shopkit/CLAUDE.md

TOTAL: 58 / 100
```

Your word count and score differ. The first three rows of the checker output should say `PASS`.

> **The checker names missing facts?** Each one is worth 3 of the 15 points. Add a line that keeps the fact. Any wording works.
>
> **You kept the contradiction and picked the wrong side?** A line that tells Claude to run `nosetests` instead of `pytest` scores zero on both the stale row and the test-command fact. Keep the instruction that is still true.
>
> **You trimmed `original/CLAUDE.md` by mistake?** Restore it: `cp $FILES/lab6-context/original/CLAUDE.md original/CLAUDE.md`.

---

## Step 4: Trim the plugin descriptions

Every command and agent in an enabled plugin puts its description in the context window on every turn. A shorter description can stop a command being chosen, so you test after you shorten.

List the description lengths in characters:

```bash
cd ~/work/lab6-context
for f in shopkit-plugin/commands/*.md shopkit-plugin/agents/*.md; do printf '%s  ' "$f"; grep -m1 '^description:' "$f" | cut -c14- | tr -d '\n' | wc -c; done
```

**Expected output:**

```
shopkit-plugin/commands/price-check.md  522
shopkit-plugin/commands/refund-policy.md  411
shopkit-plugin/commands/stock-report.md  452
shopkit-plugin/agents/cart-reviewer.md  410
```

**Your task:** rewrite the `description:` line in each of the four files, so that each description:

- is 200 characters or fewer. This is a lab rule of thumb, not a product limit
- is at least 40 characters
- still names its topic: price, stock, refund or cart

Lead with the job and the trigger. Cut the filler. The description is the line in each file that starts with `description:`. In the agent file, leave the `name:`, `model:` and `tools:` lines as they are.

Open one file:

```bash
nano shopkit-plugin/commands/price-check.md
```

The `description:` line is line 2. **Ctrl+K** cuts the line. Type the new line, starting with `description: `. Repeat for the other three files.

<details>
<summary>Show four shorter description lines</summary>

In `commands/price-check.md`:

```
description: Check a cart's price and that money is stored as integer cents.
```

In `commands/refund-policy.md`:

```
description: Answer a refund or returns question from docs/refund-policy.md.
```

In `commands/stock-report.md`:

```
description: Write a short stock report for the warehouse from docs/stock.csv.
```

In `agents/cart-reviewer.md`:

```
description: Review changed cart and pricing code, including that money is integer cents.
```

</details>

<details>
<summary>Show a prompt you can give Claude</summary>

Start Claude Code in `~/work/lab6-context` and type:

```
Shorten the description line in each file under shopkit-plugin/commands and shopkit-plugin/agents to 200 characters or fewer. Lead with the job and the trigger, and keep the topic word: price, stock, refund or cart. Change nothing else in the files.
```

Then run the length command above yourself.

</details>

Check the lengths and the score:

```bash
cd ~/work/lab6-context
python3 check_lab6.py | tail -1
```

**Expected output** with the lines from the reveal:

```
TOTAL: 70 / 100
```

Your score differs. The description rows should all say `PASS`.

**Test that the commands are still chosen.** Start a session with the plugin loaded:

```bash
cd ~/work/lab6-context/shopkit
claude --plugin-dir ../shopkit-plugin
```

Ask a matching question, then an unrelated one:

```
Is the total that price_cart returns for a cart of three items at 250 cents each correct?
```

```
What does the word "idempotent" mean?
```

For the matching question, Claude should use the plugin's `price-check` command or read `src/shop/pricing.py` as the command says. For the unrelated question, it should answer directly. Type `/exit` when you finish.

> **A description is shorter and the command stopped being chosen?** Add the trigger back in fewer words. Name what the user asks for, such as "a refund or returns question".
>
> **The checker says a description lost its topic?** Put the topic word back: price, stock, refund or cart.
>
> **You cut one too far?** `original-plugin/` holds the untouched copy. Restore one file: `cp $FILES/lab6-context/original-plugin/commands/price-check.md shopkit-plugin/commands/price-check.md`.

---

## Step 5: Measure after

Record the same three numbers again. Use the same setup as in Step 2, so the comparison is fair.

Restart Claude Code in the project folder, with no plugin flag. Do not reuse the session from Step 4:

```bash
cd ~/work/lab6-context/shopkit
claude
```

Type `/context all`. Write down the startup total and the `CLAUDE.md` line. Type `/exit`. Then run the plugin command again:

```bash
claude --plugin-dir ../shopkit-plugin plugin details shopkit-helpers
```

Write down the `Always-on` figure under `Projected token cost`.

Open `measure.csv` and fill the three `2_after` rows:

```bash
cd ~/work/lab6-context
nano measure.csv
```

Check the score:

```bash
python3 check_lab6.py | tail -3
```

**Expected output** with the files from the reveals:

```
[FAIL]  0/15 RULES-LEARNED.md has exactly two numbered rules, each with a because clause  -> found 0 numbered rule(s) in the rules list; write exactly two

TOTAL: 85 / 100
```

Only the rules row is open. Compare your before and after numbers. At least two of the three must be lower after than before.

> **The numbers did not change?** Compare like with like. `/context` also counts other files that loaded.
>
> **`measure.csv` still reports a blank row?** The checker matches the six rows that shipped: a startup total, a `CLAUDE.md` line and a plugin token cost, before and after. It names the one still missing. Extra rows of your own do not replace one of the six.

---

## Step 6: Write two rules

Open `RULES-LEARNED.md`:

```bash
nano RULES-LEARNED.md
```

**Done when** it holds **exactly two numbered rules** for your own team. Each rule:

- starts with a verb
- is one sentence
- ends with a "because" clause that points at something you measured in this lab

`1.` and `1)` both count. A rule may wrap onto an indented second line. Put evidence or notes under a heading below the two rules. Write them as prose or `-` bullets. The checker reads any numbered line with a "because" clause as a rule, wherever it sits in the file.

Do not quote a number from memory. Quote a number you measured, or link to the documentation.

<details>
<summary>Show example rules</summary>

These show the shape. Write your own, with your own measurements:

```
1. Review CLAUDE.md every quarter and delete anything stale, because stale instructions sit in the context window at every start and can contradict current ones.
2. Keep every plugin description under two sentences, because the descriptions load on every turn, and recheck the plugin with an eval after shortening one.
```

</details>

> **A third numbered line is read as a third rule?** It has a "because" in it. Turn evidence notes into `-` bullets or prose.
>
> **Your rules have no measurement behind them?** Change the because clause to something you saw in Steps 2 to 5.

---

## Step 7: Check it

Run the checker from the lab folder:

```bash
cd ~/work/lab6-context
python3 check_lab6.py
```

**Expected output** with the files from the reveals:

```
LAB 6 SCORE (local checks)
[PASS] 15/15 CLAUDE.md is at least 40 percent shorter (652 to 65 words, 90 percent)
[PASS] 15/15 The facts that must survive are still in CLAUDE.md
[PASS] 10/10 No stale instruction remains
[PASS] 12/12 Every description is 200 characters or fewer
[PASS]  6/6  No description is shortened to nothing (40+ characters)
[PASS] 12/12 Every description still names its trigger topic
[PASS] 15/15 measure.csv has a value in all six rows
[PASS] 15/15 RULES-LEARNED.md has exactly two numbered rules, each with a because clause

TOTAL: 100 / 100
```

Your word counts differ. Fix any `[FAIL]` line. Each one says what it could not accept.

**Checkpoint:** the checker reports at least 85, and `measure.csv` shows a lower number after than before for at least two of the three measurements.

The checker cannot read `/context` output, so the measurement rows are self-reported. Your facilitator may ask to see a screen.

---

## What you built

You:

- Measured what loads into the context window at startup, and what a plugin adds
- Cut a `CLAUDE.md` by at least 40 percent and kept the five facts Claude needs
- Shortened four plugin descriptions and tested that the commands are still chosen
- Measured again and compared like with like
- Wrote two rules, each tied to a measurement

## How the score is made

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

The five-facts row gives 3 points per fact, so one missing fact costs 3. Every other row is all or nothing.

## Cleanup

Nothing needs undoing. Your working folder is `~/work/lab6-context`.
