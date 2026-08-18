**No new failures — 1 continuing server-side 500 (IndexOutOfBoundsException) in the QuotaGroup delete path.**

_Likely cause: continuing server-side 500 on DELETE dk-project-quota-group-rest QuotaGroup — a product bug, not infra; no commit deployed tonight maps to it._

- 0 new; 1 continuing server 500 (IndexOutOfBoundsException) on DELETE QuotaGroup — product bug, not infra.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9474063)
