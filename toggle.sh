#!/bin/bash
# Mobile mode switch. Two flag files, no daemon, no state to corrupt:
#   ~/.claude/.mobile-mode          -- inject the guidance on every prompt
#   ~/.claude/.mobile-mode-enforce  -- also let the Stop hook block a turn
#
# Both hooks read these at fire time, so changes take effect on the very next
# turn. No session restart, and nothing to remember to undo on the Mac.

set -u

FLAG="$HOME/.claude/.mobile-mode"
ENFORCE="$HOME/.claude/.mobile-mode-enforce"

status() {
    if [ -f "$FLAG" ]; then
        if [ -f "$ENFORCE" ]; then
            echo "mobile mode: ON (enforced — Stop hook will block a turn with no options)"
        else
            echo "mobile mode: ON (guidance only)"
        fi
    else
        echo "mobile mode: OFF"
    fi
}

case "${1:-status}" in
    on)
        touch "$FLAG"
        status
        ;;
    off)
        rm -f "$FLAG" "$ENFORCE"
        status
        ;;
    enforce)
        touch "$FLAG" "$ENFORCE"
        status
        ;;
    relax)
        rm -f "$ENFORCE"
        status
        ;;
    status)
        status
        ;;
    *)
        echo "usage: toggle.sh [on|off|enforce|relax|status]" >&2
        exit 64
        ;;
esac
