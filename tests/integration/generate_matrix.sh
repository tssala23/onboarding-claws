#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
test_root=$(mktemp -d)
trap 'rm -rf "$test_root"' EXIT

roles=(general_management finance operations marketing technology engineering)
styles=(executive concise analytical conversational)

for persona in "${roles[@]}"; do
  for style in "${styles[@]}"; do
    output="$test_root/${persona}-${style}"
    ANSIBLE_CONFIG="$repo_root/ansible.cfg" ansible-playbook \
      "$repo_root/playbooks/generate-claw.yml" \
      -e 'preferred_name=Taylor' \
      -e "role=$persona" \
      -e 'day_start=08:30' \
      -e 'timezone=America/New_York' \
      -e '{"current_focus":["Validate the enterprise briefing"],"key_contacts":[{"directory_id":"contact-1","display_name":"Example Person","email":"person@example.com"}],"connectors":["outlook-mail","outlook-calendar","slack"]}' \
      -e "communication_style=$style" \
      -e "claw_output_dir=$output" >/dev/null

    test -s "$output/CLAW.md"
    test -s "$output/BOOTSTRAP.md"
    test -s "$output/workspace/skills/enterprise-briefing/SKILL.md"
    grep -q 'morning-executive-brief' "$output/CLAW.md"
    grep -q '0 8 \* \* 1,2,3,4,5' "$output/CLAW.md"
  done
done

echo "Generated and verified all 24 persona/style combinations."
