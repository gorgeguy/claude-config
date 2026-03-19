#!/usr/bin/env bash
#
# See https://code.claude.com/docs/en/statusline.md
#
input=$(cat)

#MODEL=$(echo "$input" | jq -r '.model.display_name')
#PERCENT_USED=$(echo "$input" | jq -r '.context_window.used_percentage // 0')

#echo "[$MODEL] ctx:${PERCENT_USED}%"
#echo "ctx:${PERCENT_USED}%"
echo $input | jq -r '"ctx:\(.context_window.used_percentage // 0)% in:\(.context_window.total_input_tokens) out:\(.context_window.total_output_tokens)"'

