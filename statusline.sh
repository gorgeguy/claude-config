#!/usr/bin/env bash
#
# See https://code.claude.com/docs/en/statusline.md
#
input=$(cat)

#MODEL=$(echo "$input" | jq -r '.model.display_name')
#PERCENT_USED=$(echo "$input" | jq -r '.context_window.used_percentage // 0')

#echo "[$MODEL] ctx:${PERCENT_USED}%"
#echo "ctx:${PERCENT_USED}%"
CTX=$(echo "$input" | jq -r '(.context_window.used_percentage // 0) | round')
FIVE_H=$(echo "$input" | jq -r '(.rate_limits.five_hour.used_percentage // "-") | if type == "number" then round else . end')
FIVE_H_RESETS=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
SEVEN_D=$(echo "$input" | jq -r '(.rate_limits.seven_day.used_percentage // "-") | if type == "number" then round else . end')
SEVEN_D_RESETS=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# Format a Unix epoch portably: GNU date uses -d @EPOCH (Linux), BSD date uses -r EPOCH (macOS).
# On GNU, -r means "use this FILE's mtime", so the macOS form silently fails there.
epoch_fmt() { date -d "@$1" +"$2" 2>/dev/null || date -r "$1" +"$2"; }

if [[ -n "$FIVE_H_RESETS" ]]; then
  FIVE_H_RESET=$(epoch_fmt "$FIVE_H_RESETS" "%H:%M")
else
  FIVE_H_RESET="-"
fi

if [[ -n "$SEVEN_D_RESETS" ]]; then
  SEVEN_D_RESET=$(epoch_fmt "$SEVEN_D_RESETS" "%a %H:%M")
else
  SEVEN_D_RESET="-"
fi

echo "ctx:${CTX}%  5h:${FIVE_H}% (${FIVE_H_RESET})  7d:${SEVEN_D}% (${SEVEN_D_RESET})"

