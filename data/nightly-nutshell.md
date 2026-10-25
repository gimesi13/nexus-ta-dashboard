**1 new Quota failure from a 30s cross-service feasibility timeout in QA**

_Likely cause: QA environment/timing — sold-quota lock timed out after 30s (feasibility-not-ready, cross-service lag); no build or QA-deploy changes to blame._

- 1× Quota (new) — setSoldQuotaLocked failed after 30s: feasibility-not-ready / cross-service lag (infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9634803)
