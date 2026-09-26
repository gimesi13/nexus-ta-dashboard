**5 new QuotaGroup scheduling fails — backend 500 (missing lineItemGuid) surfaced by TA test re-point NXS-13489, not infra**

_Likely cause: TA test-module commit NXS-13489 (gergely.gimesi) re-pointed expected-red scheduling tests at EOS-linked bug tickets, surfacing a known backend 500; not infra, and no QA product deploy maps to quota-group-rest._

- 5× new: HTTP 500 `IllegalStateException: missing lineItemGuid` on quotaGroups/{}/core/changeStatus?START — genuine server error, not infra
- NXS-13489 (gergely.gimesi, test-only) surfaced these; no QA-deployed product service maps to dk-project-quota-group-rest

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9545174)
