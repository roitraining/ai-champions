#!/usr/bin/env bash
# Checks a Linux class machine for everything the labs need. Reads only; changes nothing.
# Usage: bash check_env.sh
# Exit code 0 when every REQUIRED item is present, 1 otherwise.

fail=0
ok()   { printf '[ ok ] %s\n' "$1"; }
bad()  { printf '[FAIL] %s\n' "$1"; fail=1; }
warn() { printf '[warn] %s\n' "$1"; }

[ "$(uname -s)" = "Linux" ] && ok "Linux" || warn "Not Linux. The labs are written for Linux class machines."

if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    ok "python3 $(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
  else
    bad "python3 is older than 3.11"
  fi
else
  bad "python3 not found"
fi

command -v jq >/dev/null 2>&1 && ok "jq" || bad "jq not found. Install: sudo apt-get install jq   (or: sudo dnf install jq)"
command -v git >/dev/null 2>&1 && ok "git $(git --version | awk '{print $3}')" || bad "git not found"
command -v claude >/dev/null 2>&1 && ok "claude $(claude --version 2>/dev/null | head -1)" || bad "claude not found on PATH"

if command -v bwrap >/dev/null 2>&1; then ok "bubblewrap (bwrap)"; else bad "bubblewrap not found. Install: sudo apt-get install bubblewrap socat   (or: sudo dnf install bubblewrap socat)"; fi
command -v socat >/dev/null 2>&1 && ok "socat" || bad "socat not found (see the bubblewrap line for the install command)"

# Report BOTH controls. Measured on the class image 2026-11-15, all four combinations:
# the sandbox needs the AppArmor profile disabled AND
# kernel.apparmor_restrict_unprivileged_userns = 0. With only the profile cleared,
# commands run UNSANDBOXED behind one warning - and an earlier version of this block
# printed [ ok ] in exactly that state. A check that says you are protected when you are
# not is worse than no check.
aa_prof="blocking"
if [ -e /etc/apparmor.d/disable/bwrap-userns-restrict ]; then
  aa_prof="clear"
elif [ ! -e /etc/apparmor.d/bwrap-userns-restrict ]; then
  aa_prof="clear"
fi
aa_sysctl="absent"
if [ -r /proc/sys/kernel/apparmor_restrict_unprivileged_userns ]; then
  aa_sysctl="$(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null)"
fi
if [ "$aa_prof" = "clear" ] && [ "$aa_sysctl" != "1" ]; then
  ok "sandbox: profile clear, sysctl $aa_sysctl - nothing is blocking it"
  warn "  verify for real: in a session, 'touch ~/sandbox-probe' must FAIL"
else
  warn "sandbox: profile $aa_prof, apparmor_restrict_unprivileged_userns $aa_sysctl"
  if [ "$aa_prof" = "clear" ]; then
    warn "  the profile alone is NOT enough - in this state commands run UNSANDBOXED"
  fi
  warn "  Labs 2, 3 and 4 and Demos 3 and 9 need it. Switch both with:"
  warn "    bash \$FILES/setup/classroom-sandbox.sh --on     (and --off afterwards)"
  warn "  Read Lab 3 Step 1 first: it is machine-wide, so it is a decision, not a fix."
fi

echo
echo "Sandbox probe (run this INSIDE a Claude Code session, with the sandbox on, from the Bash tool):"
echo "  touch ~/sandbox-probe"
echo "Expected with the sandbox working: it fails with 'Read-only file system'."
echo "If it succeeds, remove the file (rm ~/sandbox-probe) and tell your instructor: the sandbox is not active."

[ -n "$ANTHROPIC_API_KEY" ] && warn "ANTHROPIC_API_KEY is set. Claude Code may use it instead of your seat login. Run: unset ANTHROPIC_API_KEY, then /status in Claude Code."

echo
[ $fail -eq 0 ] && echo "All required items present." || echo "Fix the FAIL lines before the labs."
exit $fail
