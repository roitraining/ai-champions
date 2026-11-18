# shopkit

Welcome to shopkit! This file tells Claude Code everything it could ever want to know about this project. Please read all of it carefully, every time, before doing anything. We care a great deal about quality and we want every change to be excellent, thoughtful, careful and well considered.

## About the project

shopkit is a small library that prices shopping carts for a fictional online store. It was started in 2019 by a team that has since moved on to other projects. It started as a Python 2 script, and then it was ported to Python 3, and then it was cleaned up, and then it was refactored. The history is long and interesting but you do not need to know it. The store sells pallet wrap, shipping labels and tape.

## Very important rules (please read twice)

- Run the tests with `nosetests` before you finish any change.
- Run the tests with `python3 -m pytest -q` before you finish any change.
- Never commit the `.env` file. It holds a database password. Never, ever commit it. Really never.
- Money values are stored as integer cents, never as floats. Do not use floats for money. Floats are not allowed for money.
- The public API lives in `src/shop/api.py`. Do not change function names in the public API without asking.
- Always write code that is clean, readable, well structured and well documented.

## Build and deploy

The build runs on our Jenkins server. Jenkins builds every commit and posts to the team chat. If Jenkins is red, fix it first. Deployment used to happen through the legacy FTP uploader in `tools/ftp_upload.py`, which pushes the build to the old web host. Remember to run the FTP uploader after a release. (The FTP uploader was deleted in 2022 and the old host is gone, but this paragraph is still here.)

## Python version

shopkit supports Python 2.7 and Python 3. When writing code, make sure it runs on Python 2.7 with `from __future__ import print_function`. Python 2.7 support is very important to us.

## Style guide

- Use 4 spaces for indentation. Do not use tabs. Tabs are not allowed.
- Use 4 spaces for indentation (this is the same rule as above, repeated for emphasis).
- Keep lines under 100 characters. Keep lines short. Short lines are easier to read.
- Name functions with lowercase words joined by underscores. Name classes in CapWords. Name constants in capital letters. Name modules in lowercase.
- Write a docstring for every function. A docstring should say what the function does, what its arguments are, what it returns and what it raises. A docstring should be a complete sentence. A docstring should not be too long. A docstring should not be too short.
- Import standard library modules first, then third-party modules, then local modules, with a blank line between the groups.
- Do not leave commented-out code in the repository. Do not leave print statements in the repository.

## File layout

```
shopkit/
  CLAUDE.md
  src/
    shop/
      __init__.py
      api.py
      pricing.py
      cart.py
  tests/
    test_pricing.py
    test_cart.py
  tools/
    ftp_upload.py
  build/
  docs/
  README.md
```

## How to be a good assistant

Be helpful. Be kind. Think step by step. Take your time. Check your work. If you are not sure, ask. Explain your reasoning. Write good commit messages. Be concise but also be thorough. Always double check. Remember that quality matters and that the team is counting on you to do an excellent job on every single task, no matter how small it seems.

## Team contacts

Questions about pricing go to the pricing team. Questions about the cart go to the cart team. Questions about builds go to whoever is on call this week. If nobody is on call, ask in the team chat.

## Reminder

Never commit the `.env` file. Run the tests. Money is integer cents. Thank you for reading all of this.
