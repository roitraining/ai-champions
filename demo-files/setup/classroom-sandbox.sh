#!/usr/bin/env bash
# Turn the Claude Code sandbox on for this class machine, and turn it back off.
# Labs 3 and 4 need a working sandbox. Run --check first; it changes nothing.
#
#   bash $FILES/setup/classroom-sandbox.sh --check     is the sandbox blocked? (changes nothing, no sudo)
#   bash $FILES/setup/classroom-sandbox.sh --on        let the sandbox start (needs sudo)
#   bash $FILES/setup/classroom-sandbox.sh --off       put the machine back as you found it
#
# TWO THINGS BLOCK THE SANDBOX, AND YOU NEED BOTH CLEARED
#
# On Ubuntu 24.04 and later, Claude Code's sandbox is built on bubblewrap, which needs to
# create a nested user namespace. Two separate controls stop it:
#
#   1. the AppArmor profile  bwrap-userns-restrict
#   2. the sysctl            kernel.apparmor_restrict_unprivileged_userns = 1
#
# Measured on the class image, 2026-11-15, all four combinations:
#
#   profile   sysctl   result
#   active    1        every sandboxed command fails with apply-seccomp   (the default)
#   DISABLED  1        RUNS UNSANDBOXED behind one warning - the dangerous case
#   active    0        apply-seccomp, exactly as the default
#   DISABLED  0        works: writes blocked, disallowed network blocked
#
# The second row is why this script now handles both. With only the profile disabled, a
# configuration that does not set `failIfUnavailable` runs your commands **unsandboxed**
# behind a single warning, and an earlier version of this script reported "the sandbox can
# start" in exactly that state. It could not. A check that says you are protected when you
# are not is worse than no check.
#
# An earlier note here said the sysctl "does nothing". That came from a sister course and
# is true only in isolation: changing it alone leaves the profile blocking. Both must go.
#
# WHY YOU WOULD NOT DO THIS AT WORK
#
# `--on` disables a machine-wide AppArmor profile and relaxes a machine-wide sysctl. It
# does not grant anything to Claude Code specifically - every process on the box gains
# what it lifts. The narrower options do not work: the denial is raised inside
# `unpriv_bwrap`, the profile `/usr/bin/bwrap` transitions into, so confining the calling
# binary changes nothing about what its child transitions to.
#
# That trade - weaken a machine-wide control to switch on one application's sandbox - is
# the kind of decision this course is about, and on a production fleet the answer is
# usually no. It is defensible HERE because this is a disposable single-purpose classroom
# VM holding nothing but fake credentials, and because the alternative is being unable to
# run the exercise that teaches you what the sandbox does. Make the same call on a
# developer's laptop or a build server and you have traded a real control for convenience.
#
# Run `--off` when you are finished. A reboot also restores both defaults.

set -u
# Messages below use $0, never $FILES. $FILES is a convention in the lab text, not an
# exported variable, so under `set -u` an echo containing it aborts the script. Run 1 on
# the class image hit exactly that: --check died with "FILES: unbound variable" and exit 1,
# swallowing the line that tells the student how to switch the sandbox on.
PROFILE="/etc/apparmor.d/bwrap-userns-restrict"
DISABLE_LINK="/etc/apparmor.d/disable/$(basename "$PROFILE")"
SYSCTL_KEY="kernel.apparmor_restrict_unprivileged_userns"
SYSCTL_PATH="/proc/sys/kernel/apparmor_restrict_unprivileged_userns"
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
# Non-interactive variant for read-only probes: never blocks on a password prompt.
SUDO_N=""; [ "$(id -u)" -ne 0 ] && SUDO_N="sudo -n"

case "${1:-}" in --check|--on|--off) MODE="$1" ;; *)
  sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
  exit 2 ;;
esac

if [ "$(uname -s)" != "Linux" ]; then
  echo "This script is for Linux. On macOS the sandbox uses Seatbelt and needs no change."
  exit 1
fi

# --check advertises "changes nothing, no sudo", so it must never sit at a password
# prompt. sudo -n fails immediately instead of waiting.
loaded() { $SUDO_N aa-status 2>/dev/null | grep -q 'unpriv_bwrap'; }

# Reads without sudo. Prints the value, or "absent" where the kernel has no such knob.
sysctl_val() { [ -r "$SYSCTL_PATH" ] && cat "$SYSCTL_PATH" 2>/dev/null || echo absent; }

profile_blocking() {
  if [ -L "$DISABLE_LINK" ]; then return 1; fi          # explicitly disabled
  if [ -e "$PROFILE" ] || loaded; then return 0; fi     # present or loaded
  return 1
}

sysctl_blocking() { [ "$(sysctl_val)" = "1" ]; }

report() {
  local p s
  if profile_blocking; then p="BLOCKING"; else p="clear"; fi
  s="$(sysctl_val)"
  echo "  AppArmor profile bwrap-userns-restrict : $p"
  echo "  $SYSCTL_KEY : $s"
  if profile_blocking || sysctl_blocking; then
    echo "[INFO] The sandbox CANNOT start on this machine yet."
    if profile_blocking && sysctl_blocking; then
      echo "       Both controls are still on."
    elif profile_blocking; then
      echo "       The profile is still blocking."
      echo "       Sandboxed Bash calls fail with 'apply-seccomp ... Permission denied'."
      echo "       That is a platform limit, not a mistake in your configuration."
    else
      echo "       The sysctl is still 1, and the profile alone is NOT enough."
      echo "       In this exact state commands do not error - they run UNSANDBOXED,"
      echo "       behind a single warning. Nothing protects you and nothing says so."
      echo "       This is the worst of the four states, which is why --check reports it."
    fi
    echo "       Switch it off for this lab with: bash $0 --on"
  else
    echo "[ OK ] Nothing is blocking the sandbox - both controls are clear."
    echo "       Confirm it for real inside a session: ask Claude to run 'touch ~/sandbox-probe'."
    echo "       It should fail with 'Read-only file system'. If it succeeds, you are NOT sandboxed."
    echo "       Put the machine back with: bash $0 --off"
  fi
}

case "$MODE" in
  --check) report ;;

  --on)
    changed=0
    if [ -L "$DISABLE_LINK" ]; then
      echo "[ OK ] profile already disabled."
    else
      $SUDO mkdir -p "$(dirname "$DISABLE_LINK")" || exit 1
      $SUDO ln -sf "$PROFILE" "$DISABLE_LINK" || exit 1
      if $SUDO apparmor_parser -R "$PROFILE" 2>/dev/null; then
        echo "[ OK ] disabled bwrap-userns-restrict."
        changed=1
      else
        $SUDO rm -f "$DISABLE_LINK"
        echo "[FAIL] apparmor_parser could not unload the profile. Nothing was changed."
        echo "       Check you have sudo, then tell your instructor."
        exit 1
      fi
    fi
    if [ "$(sysctl_val)" = "1" ]; then
      if $SUDO sysctl -w "$SYSCTL_KEY=0" >/dev/null 2>&1; then
        echo "[ OK ] set $SYSCTL_KEY=0."
        changed=1
      else
        echo "[FAIL] could not set $SYSCTL_KEY=0."
        echo "       The profile alone is NOT enough: commands would run unsandboxed."
        echo "       Run 'bash $0 --off' to undo the profile change, and tell your instructor."
        exit 1
      fi
    else
      echo "[ OK ] $SYSCTL_KEY is already $(sysctl_val)."
    fi
    echo
    echo "Both controls are clear. This is machine-wide - see the notes at the top of this file."
    echo "Verify inside a session: ask Claude to run 'touch ~/sandbox-probe'; it must FAIL."
    echo "Undo with: bash $0 --off"
    [ "$changed" = "1" ] || true ;;

  --off)
    rc=0
    if [ -L "$DISABLE_LINK" ]; then
      $SUDO rm -f "$DISABLE_LINK"
      if $SUDO apparmor_parser -r "$PROFILE" 2>/dev/null; then
        echo "[ OK ] re-enabled bwrap-userns-restrict."
      else
        echo "[WARN] could not reload the profile. Reboot to restore the default."
        rc=1
      fi
    else
      echo "[ OK ] profile was not disabled by this script."
    fi
    if [ "$(sysctl_val)" = "0" ]; then
      if $SUDO sysctl -w "$SYSCTL_KEY=1" >/dev/null 2>&1; then
        echo "[ OK ] restored $SYSCTL_KEY=1."
      else
        echo "[WARN] could not restore $SYSCTL_KEY. Reboot to restore the default."
        rc=1
      fi
    fi
    echo "The machine is as you found it. Confirm with: bash $0 --check"
    exit $rc ;;
esac
