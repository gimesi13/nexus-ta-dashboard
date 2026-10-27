**5 new failures — a backend validation regression on quotaGroups/optionAssembler (4 Lookup) plus one flaky Quota lock timeout.**

_Likely cause: backend validation regression — POST quotaGroups/optionAssembler now returns 400 'selectionMode must not be null' (4 Lookup); not infra. No commit maps to the endpoint, so attribute in TeamCity._

- 4× Lookup — HTTP 400 'selectionMode must not be null' on quotaGroups/optionAssembler (backend validation regression, not infra)
- 1× Quota — soldQuota lock timed out after 30s on cross-service feasibility lag (likely flaky)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9637155)
