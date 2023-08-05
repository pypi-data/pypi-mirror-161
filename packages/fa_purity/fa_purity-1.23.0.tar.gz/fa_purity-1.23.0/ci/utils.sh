# shellcheck shell=bash

function build {
  local input="${1}"
  nix build --print-build-logs --json "${input}" \
    | jq -r '.[].outputs | to_entries[].value' \
    | cachix push fa-foss
}
