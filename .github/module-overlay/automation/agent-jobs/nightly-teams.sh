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
# Flow: fetch TC summary → regenerate nightly.json → post Adaptive Card.
set -euo pipefail
cd "$(dirname "$0")/../.."

export TEAMCITY_URL="${TEAMCITY_URL:-https://teamcity.dynata.com}"
export TEAMCITY_NIGHTLY_BUILD_TYPE_ID="${TEAMCITY_NIGHTLY_BUILD_TYPE_ID:-Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt}"

echo "==> Fetch TeamCity nightly summary"
if [[ -z "${TEAMCITY_TOKEN:-}" ]]; then
  echo "TEAMCITY_TOKEN unset — cannot build the card."
  exit 1
fi
python3 automation/tc_fetch_nightly.py

echo "==> Regenerate nightly.json"
python3 dashboard/tools/generate_nightly.py

echo "==> Post nightly status card to Teams"
python3 automation/post_nightly_teams.py

echo "==> Nightly Teams card job done"
