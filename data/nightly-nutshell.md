**2 new QA-side failures (Quota, QuotaGroup) — no code changes in the window to blame.**

_Likely cause: QA backend/environment instability — a FeasibilityDataStore 500 and a 30s cross-service lag timeout; no test or QA-deploy commits in the window._

- Quota lock timed out (30s cross-service lag) and QuotaGroup calculateAdhoc hit HTTP 500 — both QA-side.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9651087)
