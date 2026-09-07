---
description: Turn mobile mode on or off (tappable options + push after every turn)
argument-hint: on | off | enforce | relax | status
allowed-tools: Bash(bash:*)
---

Mobile mode switch. Result of running the toggle:

!`bash ~/.claude/skills/mobile-mode/toggle.sh $ARGUMENTS`

Report that line back to the user verbatim and stop. Do not explain the modes
unless asked — if the toggle printed a status, they already know what they got.
