#!/usr/bin/env python3
"""UserPromptSubmit hook: append mobile-mode guidance to this one turn.

This is the Claude Code analogue of what Happy (github.com/slopus/happy) does in
`packages/happy-app/sources/sync/sync.ts` -- it attaches an `appendSystemPrompt`
to the *message* rather than the session, so the instruction only rides along on
turns that actually came from a phone.

We can't detect origin the way Happy can (it injects client-side, in the app;
nothing in the hook's stdin JSON or the process env marks a local session as
being driven by Remote Control), so the switch is an explicit flag file instead.

Silence is the safe default: any unexpected condition prints `{}` and the turn
proceeds untouched.
"""

import json
import os
import sys

FLAG = os.path.expanduser("~/.claude/.mobile-mode")

GUIDANCE = """\
<mobile-mode>
The user has mobile mode on: they are driving this session from their phone, away
from the terminal. Reading is cheap for them, typing is expensive, tapping is free.

1. END THE TURN WITH OPTIONS. If there is a real next step or a decision that is
   genuinely theirs, finish by calling AskUserQuestion with those as options
   instead of describing them in prose. Keep each option to a few words and make
   them actually distinct.
   Do NOT manufacture a question to satisfy this. A turn that truly finishes the
   work should just end. A question whose answer would not change what you do
   next is worse than no question.

2. NOTIFY WHEN THE TURN ENDS. Call PushNotification once, at the end. One line,
   leading with what they would act on -- "auth tests failing, 2 of 14" beats
   "task complete". The tool suppresses itself if they are actually at the
   terminal, so this is safe to call even when mobile mode is on by mistake.

3. WRITE FOR A PHONE SCREEN. Lead with the answer. Cut the preamble. Long tables
   and wide code blocks do not survive the trip.
</mobile-mode>"""


def main() -> None:
    try:
        if not os.path.exists(FLAG):
            print("{}")
            return

        # Read and discard stdin: the hook contract expects us to drain it, and
        # leaving it unread can surface as a broken pipe on the writing side.
        sys.stdin.read()

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": GUIDANCE,
            }
        }))
    except Exception:
        # Never let this hook break a turn. A missing nudge is a small loss; a
        # hook that errors on every prompt is a broken session.
        print("{}")


if __name__ == "__main__":
    main()
