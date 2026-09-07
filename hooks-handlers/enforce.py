#!/usr/bin/env python3
"""Stop hook: optionally refuse to end a mobile-mode turn that offered no options.

OFF BY DEFAULT. Requires BOTH ~/.claude/.mobile-mode and
~/.claude/.mobile-mode-enforce to exist. The injected guidance in inject.py is
usually enough; this exists for when it isn't.

Happy could only ask nicely -- it had a system prompt and no way to check the
result. A Stop hook can actually verify, at the cost of being able to nag about
a turn that had nothing worth asking. That trade is why this is opt-in.

Recursion guard: Claude Code caps how many times a Stop hook may block a turn
and states plainly, "For Stop/SubagentStop hooks, check stop_hook_active in the
input and return success while it's true." We honor that before anything else.
"""

import json
import os
import sys

FLAG = os.path.expanduser("~/.claude/.mobile-mode")
ENFORCE = os.path.expanduser("~/.claude/.mobile-mode-enforce")

REASON = (
    "Mobile mode is on and this turn ended without offering the user anything to "
    "tap. If there is a real next step or a decision that is theirs to make, call "
    "AskUserQuestion with those as options now. If the work is genuinely finished "
    "and there is nothing worth asking, say so in one short line and stop -- do "
    "not invent a question."
)


def offered_options(transcript_path: str) -> bool:
    """Did the assistant call AskUserQuestion since the last real user message?

    Walks the transcript backwards and stops at the first user message that is
    actual user input. Tool results also arrive with role "user", so those are
    skipped -- treating one as the turn boundary would truncate the window and
    make us miss a tool call that did happen.
    """
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        # No readable transcript means no evidence. Absence of evidence is not
        # grounds to block a turn.
        return True

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue

        message = entry.get("message") or {}
        role = message.get("role") or entry.get("type")
        content = message.get("content")

        if role == "assistant" and isinstance(content, list):
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == "AskUserQuestion"
                ):
                    return True

        if role == "user":
            if isinstance(content, str):
                return False  # plain text: this is the turn boundary
            if isinstance(content, list):
                is_tool_result = any(
                    isinstance(b, dict) and b.get("type") == "tool_result"
                    for b in content
                )
                if not is_tool_result:
                    return False

    return False


def main() -> None:
    try:
        if not (os.path.exists(FLAG) and os.path.exists(ENFORCE)):
            print("{}")
            return

        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}

        if event.get("stop_hook_active"):
            print("{}")
            return

        transcript = event.get("transcript_path")
        if not transcript or offered_options(transcript):
            print("{}")
            return

        print(json.dumps({"decision": "block", "reason": REASON}))
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
