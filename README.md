# mobile-mode

A Claude Code plugin for people who drive sessions from their phone.

When you're on mobile, reading is cheap, typing is expensive, and tapping is free.
Claude Code doesn't know that. `mobile-mode` tells it — per turn, behind a switch,
so nothing changes when you're back at the terminal.

With it on, a turn ends with something you can tap:

- **Tappable options.** Real next steps go out as `AskUserQuestion`, which renders
  as chips in Remote Control, instead of as a paragraph you'd have to answer by
  thumb-typing.
- **A push when the turn ends.** One line, leading with what you'd act on.
- **Output written for a phone screen.** Answer first, no preamble.

## Install

```bash
/plugin marketplace add holystreetballer/claude-code-mobile-mode
/plugin install mobile-mode
```

Or clone straight into your skills directory, which auto-loads it:

```bash
git clone https://github.com/holystreetballer/claude-code-mobile-mode ~/.claude/skills/mobile-mode
```

Requires `python3` (stdlib only — no dependencies) and Claude Code 2.1.x or newer.

## Use

```
/mobile-mode:toggle on        # guidance only — the sane default
/mobile-mode:toggle enforce   # also let the Stop hook block an optionless turn
/mobile-mode:toggle relax     # back to guidance only
/mobile-mode:toggle off
/mobile-mode:toggle status
```

Flip it on when you pick up your phone, off when you sit back down. Hooks read the
switch at fire time, so it takes effect on the next turn — no restart.

## How it works

Two hooks and a flag file.

| | Event | Job |
|---|---|---|
| `hooks-handlers/inject.py` | `UserPromptSubmit` | returns `hookSpecificOutput.additionalContext` carrying the mobile guidance |
| `hooks-handlers/enforce.py` | `Stop` | *opt-in*; blocks a turn that ended without `AskUserQuestion` |

The guidance is attached to each **message**, not to the session. That's the whole
trick: it costs nothing on turns where mobile mode is off, and it can be flipped
mid-session without restarting anything.

Everything is gated on `~/.claude/.mobile-mode` existing. Every failure path —
missing flag, unreadable transcript, malformed stdin — prints `{}` and lets the
turn through untouched. A hook that breaks your session is worse than a missing
nudge.

## Why a flag file instead of detecting your phone

Because it can't be detected. A hook receives no indication of where a prompt came
from: there's no origin field in its stdin JSON, and no environment marker for a
local session being driven by Remote Control (`CLAUDE_CODE_REMOTE*` refers to cloud
sessions, which is a different thing).

That turns out to be a feature. An explicit switch means unattended sessions —
chat-channel bridges, cron jobs, anything running without a human watching — never
pick this up, which a `CLAUDE.md` instruction could not have guaranteed.

## On enforcement

`enforce` is off by default, and it should probably stay that way.

The Stop hook can verify that a turn offered options, but it cannot tell *why* one
didn't. "The model got lazy" and "the work is genuinely finished" look identical
from the outside. Try the guidance alone first; reach for `enforce` only if the
prompt proves too loose in practice.

The guidance itself is deliberately hedged: it tells the model that a question
whose answer wouldn't change what it does next is worse than no question at all.
Turn-ending options are only worth anything when they represent a real decision.

## Prior art

[Happy](https://github.com/slopus/happy) did this for Claude Code before Remote
Control existed, and the per-message design here is lifted from it: Happy attaches
`meta.appendSystemPrompt` to every message the phone sends (`sync.ts:842`), has the
model emit an `<options>` XML block, then regexes it back out client-side to render
buttons (`parseMarkdownBlock.ts:117`).

The one change is `AskUserQuestion` in place of the XML round-trip. Happy had to
invent a tag and parse it because it controls its own client; a plugin doesn't, and
`AskUserQuestion` already renders as tappable chips with nothing to parse.

## License

MIT
