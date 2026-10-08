**No new failures — 6 continuing QA backend 500s (BOS project-accept, QuotaGroup save-dates).**

_Likely cause: continuing QA backend HTTP 500s on BOS accept & QuotaGroup save-dates — not infra timeouts/502/504 and not traced to any service deployed this window._

- 3× BOS sample creation — 500 on project-accept / salesOrders (DkmsError); 2× QuotaGroup save-dates returned 500 where 400 expected

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9606062)
