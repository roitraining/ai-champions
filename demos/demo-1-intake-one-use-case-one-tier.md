# Demo 1: Intake: One Use Case, One Tier

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 12 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

A fictional team wants Claude Code to draft weekly release notes. You run the use case through a ten-section intake checklist, give it a risk tier, and name the one answer that decided the tier. Claude drafts the checklist from a written brief. You judge the draft.

## Prerequisites

- [ ] `claude auth status` shows you are signed in (see [`SETUP.md`](../SETUP.md))
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Read the brief

Open a terminal (the **Terminal Emulator** icon on the desktop). Go to the demo folder and list it:

```bash
cd $FILES/demo1-intake
ls
```

**Expected output:**

```
use-case-brief.md
```

Print the brief. It is 29 lines:

```bash
cat use-case-brief.md
```

The brief describes a team called Meridian Freight Systems. Read it once and notice what it says about data, tools, permissions and credentials. Notice what it does not say.

> **The text scrolled off the screen?** Use `less use-case-brief.md` instead. Press **Space** for the next page and **q** to quit.

---

## Step 2: Read the checklist headings and the tiers

The checklist has ten sections. List their names:

```bash
grep '^## ' ../templates/intake-checklist.md
```

**Expected output:**

```
## 1. Purpose and owner
## 2. Data
## 3. Repositories
## 4. Tools and servers
## 5. Model and effort
## 6. Permissions and sandbox
## 7. Credentials
## 8. Review and escalation
## 9. Logging
## 10. Exit criteria
## Risk tier (record the result)
```

The last heading is where the tier goes. Print the tier table:

```bash
cat ../templates/risk-tiers.md
```

The first table lists four questions, each with a Low, Medium and High answer. The rule above it: **a use case gets the highest tier that any one question puts it in.** You use this table in Step 5.

---

## Step 3: Have Claude draft the checklist

Start Claude Code in the demo folder:

```bash
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt and press Enter:

```
Read use-case-brief.md and ../templates/intake-checklist.md. Draft an answer for each of the ten sections. Write "Unknown" where the brief is silent. Do not invent facts. Save the draft to demo1-draft.md in this folder.
```

**Expected result:** Claude reads both files, writes `demo1-draft.md`, and summarizes it. The draft has ten sections. Several answers say `Unknown`, most of them in sections 5, 8, 9 and 10. Claude's wording differs on every run.

Leave Claude Code by typing `/exit` and pressing Enter. Count the `Unknown` answers in the draft:

```bash
grep -c Unknown demo1-draft.md
```

**Expected output:** a number above 0. The exact count differs between runs.

> **Claude asked to write the file, and you are not sure what to answer?** Choose the option that allows the write. The file goes in this folder only.
>
> **`demo1-draft.md` does not exist?** Claude may have printed the draft without saving it. Start `claude` again and type: `Save that draft to demo1-draft.md in this folder.`

---

## Step 4: Find one invented fact

Claude was told not to invent facts. It sometimes does. Read the draft:

```bash
less demo1-draft.md
```

Press **Space** for the next page and **q** to quit. For each section, ask: which sentence in the brief says that?

**Your task:** find one sentence in the draft that states something the brief does not say.

To check a phrase from the draft against the brief, search the brief for a word from it. Two examples:

```bash
grep -n -i reviewed use-case-brief.md
grep -n -i protect use-case-brief.md
```

**Expected output:** the first command prints the brief line that contains `reviewed`, with its line number:

```
21:**Review.** The pull request is reviewed by one other engineer. Nothing is logged except what git records.
```

The second prints nothing, because the brief never uses the word `protect`. No output means the brief does not say it. If the draft states something about protection, that sentence is a candidate. Search for a word from the sentence you doubt.

Write your finding in a notes file. Create the folder and open the file in `nano`:

```bash
mkdir -p ~/work
nano ~/work/demo1-notes.md
```

Type one line in this format. Replace the angle brackets with your finding:

```
Invented fact: section <number>, the draft said <text the brief does not support>
```

Press **Ctrl+O**, then **Enter**, to save. Press **Ctrl+X** to exit.

> **Every sentence in the draft matches the brief?** That is a valid result. Write `Invented fact: none found` and continue. Read sections 5, 8, 9 and 10 again first: the brief is silent there, so any detail is a candidate.

---

## Step 5: Give it a tier

**Your task:** use the table from Step 2. Go through its four questions for this use case:

| Question | Where the answer is in the brief |
|---|---|
| What data can Claude Code reach? | The **Data** and **Credentials** paragraphs |
| What can it change? | The **Repositories** and **Permissions** paragraphs |
| Who sees the output? | The **What the team wants** and **Review** paragraphs |
| What identity does it use? | The **Tools** and **Credentials** paragraphs |

Give each question a Low, Medium or High answer. The use case takes the highest of the four.

Add two lines to your notes:

```bash
nano ~/work/demo1-notes.md
```

```
Tier: <Low, Medium or High>
Deciding answer: section <number>, <what the answer was>. Change that would lower it: <one change>
```

Replace the angle brackets with your own answers. Save with **Ctrl+O**, **Enter**, then exit with **Ctrl+X**.

Check what you wrote:

```bash
cat ~/work/demo1-notes.md
```

<details>
<summary>Show the expected answer</summary>

**Tier:** Medium.

**Deciding answer:** section 2, Data. A real staging database password sits in `config/staging.env` inside the repository folder, and nothing stops Claude Code from reading it or from pushing.

**One change that lowers the tier:** deny reads of that file (a `Read` deny rule) and block `git push`. With the password out of reach, most of this use case is Low risk.

**Also expected:** sections 5, 8, 9 and 10 come back `Unknown` or thin. That is a result. It means the team has not decided those questions yet.

**If you chose High:** the data row of the table puts credentials in High, so your reasoning holds. Name section 2 as the deciding answer either way. The tier is an example scale, and what matters is that you can name the one answer that set it.

</details>

---

## What you saw

- An intake checklist turns "can we use Claude Code for this?" into ten repeatable questions.
- `Unknown` is a finding. It shows which decision the team has not made.
- Most of the use case was low risk. One data answer and one missing control set the tier.

Without a question list, each use case is judged by whoever is in the room. With one, a missing control is visible and you can say which one it is.

## Cleanup

Nothing on the machine changed except the files in the demo folder and `~/work/demo1-notes.md`. To remove them:

```bash
rm -f $FILES/demo1-intake/demo1-draft.md ~/work/demo1-notes.md
```
