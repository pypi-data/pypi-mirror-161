# shellcheck shell=bash

echo "Executing architecture check phase" \
  && lint-imports --config "arch.cfg" \
  && lint-imports --config "arch_test.cfg" \
  && echo "Finished architecture check phase"
