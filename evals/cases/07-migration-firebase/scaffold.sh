#!/usr/bin/env bash
# Runs only with `claude plugin eval --scaffold`. Seeds the empty workspace.
set -euo pipefail
cp -R "$(cd "$(dirname "$0")" && pwd)/fixture/." .
