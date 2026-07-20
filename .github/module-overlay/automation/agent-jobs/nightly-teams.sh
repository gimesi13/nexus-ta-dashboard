#!/usr/bin/env bash
# Morning-only Teams card for last night's Regression Tests run.
#
# Intended schedule: weekdays ~07:30 Europe/Budapest (after people wake up).
# Site refresh stays on TA Dashboard Publish (right after the nightly).
#
# Requires:
#   TEAMCITY_TOKEN (+ optional TEAMCITY_URL / TEAMCITY_NIGHTLY_BUILD_TYPE_ID)
#   NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL  (group-chat webhook; required to post)
#
# Flow: reuse the Pages-published nightly.json (summary + AI nutshell from the
# overnight TA Dashboard Publish + GHA rewrite) → post Adaptive Card. Falls back
# to fetching TeamCity + regenerating (rules nutshell) when Pages is unreachable.
set -euo pipefail
cd "$(dirname "$0")/../.."

export TEAMCITY_URL="${TEAMCITY_URL:-https://teamcity.dynata.com}"
export TEAMCITY_NIGHTLY_BUILD_TYPE_ID="${TEAMCITY_NIGHTLY_BUILD_TYPE_ID:-Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt}"

NIGHTLY_JSON="dashboard/data/nightly.json"
PAGES_JSON_URL="${NIGHTLY_JSON_URL:-https://raw.githubusercontent.com/gimesi13/nexus-ta-dashboard/main/data/nightly.json}"
mkdir -p dashboard/data

# Prefer the published nightly.json so the card carries the SAME AI nutshell the
# dashboard shows. generate_nightly.py would otherwise rebuild it without one.
if [[ "${NIGHTLY_USE_LOCAL:-0}" != "1" ]] && curl -fsSL "$PAGES_JSON_URL" -o "${NIGHTLY_JSON}.tmp"; then
  mv "${NIGHTLY_JSON}.tmp" "$NIGHTLY_JSON"
  echo "==> Using Pages nightly.json (summary + AI nutshell)"
else
  rm -f "${NIGHTLY_JSON}.tmp"
  echo "==> Pages fetch failed — regenerating from TeamCity"
  if [[ -z "${TEAMCITY_TOKEN:-}" ]]; then
    echo "TEAMCITY_TOKEN unset — cannot build the card."
    exit 1
  fi
  python3 automation/tc_fetch_nightly.py
  python3 dashboard/tools/generate_nightly.py
  # Merge the deterministic (rules) nutshell so the card still has a summary.
  python3 automation/generate_nutshell.py --merge-nightly || true
fi

echo "==> Post nightly status card to Teams"
python3 automation/post_nightly_teams.py

echo "==> Nightly Teams card job done"
