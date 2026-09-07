---
name: mobile-mode
description: Set up, explain, troubleshoot, or change what mobile mode injects — the plugin that makes Claude Code end turns with tappable AskUserQuestion options and a push notification when the user is driving the session from their phone via Remote Control. Use for "mobile mode isn't firing", "stop asking me questions on my phone", "change the mobile prompt", "why didn't I get a notification".
---

# mobile-mode

Makes a phone-driven Claude Code session end each turn with something tappable
instead of something to type.

## How it works

Two hooks and a flag file. Nothing runs unless `~/.claude/.mobile-mode` exists.

| File | Event | Job |
|---|---|---|
| `hooks-handlers/inject.py` | `UserPromptSubmit` | returns `hookSpecificOutput.additionalContext` with the mobile guidance, per turn |
| `hooks-handlers/enforce.py` | `Stop` | opt-in; blocks a turn that ended without `AskUserQuestion` |
| `toggle.sh` | — | creates/removes the flag files |

Guidance is injected per *message*, not per session, so it costs nothing on
turns where mobile mode is off, and it can be flipped mid-session.

## Switching it

`/mobile-mode:toggle on | off | enforce | relax | status`, or call `toggle.sh`
directly. `enforce` adds the Stop hook's blocking; `relax` removes it and leaves
the guidance on. Takes effect on the next turn — no restart.

## Changing what it says

Edit `GUIDANCE` in `hooks-handlers/inject.py`. It is a plain string; there is no
build step and no restart. Test it with:

```bash
echo '{}' | python3 ~/.claude/skills/mobile-mode/hooks-handlers/inject.py
```

With the flag off that prints `{}`. With it on it prints the JSON the hook feeds
to the model.

## Troubleshooting

**Nothing is being injected.** Check `toggle.sh status` first — the flag is the
whole gate. Then run the test command above; if it prints the JSON but behavior
hasn't changed, the plugin isn't loaded (`claude plugin list`).

**No push on the phone.** The push half is the `PushNotification` tool, which is
gated separately by `agentPushNotifEnabled` in `~/.claude/settings.json` (shown
in `/config` → Notifications as "Notify when Claude is done"). It also
deliberately suppresses itself when the user is active at the terminal, so a
missing notification on the desktop is correct behavior, not a fault.

**Too many questions.** That is the guidance working as written but the model
reading it too eagerly. Soften item 1 in `GUIDANCE` rather than turning the
whole thing off.

## What it deliberately does not do

It does not detect whether a prompt actually came from a phone. Nothing in the
hook's stdin JSON or the process environment marks a local session as being
driven by Remote Control — `CLAUDE_CODE_REMOTE*` refers to cloud sessions, which
is a different thing. Hence the explicit flag.

The flag is also what makes this safe to install globally. Long-running unattended
sessions — a chat-channel bridge, scheduled jobs, anything driven by cron — would
inherit an instruction placed in `~/.claude/CLAUDE.md`, and would start asking
questions and firing notifications at nobody. They never set the flag, so they
never see any of this. That is the main reason this is a plugin and not a
`CLAUDE.md` block.

## Prior art

The design is lifted from Happy (github.com/slopus/happy), which did the same
thing for Claude Code before Remote Control existed. It injected its instruction
per-message as `meta.appendSystemPrompt` (`sync.ts:842`), had the model emit an
`<options>` XML block, and regexed it back out client-side to render buttons
(`parseMarkdownBlock.ts:117`). `AskUserQuestion` replaces the XML round-trip —
it renders as tappable chips natively, so there is nothing to parse.
