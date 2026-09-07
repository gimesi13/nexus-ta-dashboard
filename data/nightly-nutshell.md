**5 new failures in Quota/Project — backend Feasibility calculation returning HTTP 400 'unavailable'.**

_Likely cause: product-side backend break — details-editor returns HTTP 400 'Feasibility Calculation unavailable!' on soldQuota/feasibility calls (not infra); no deploy commit captured to name a developer._

- 4× Quota — backend HTTP 400 'Feasibility Calculation unavailable!' on soldQuota-lock/feasibility calls
- 1× Project E2E — assertion: totalQuota 1800 ≠ expected 1900 (+100)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9510207)
