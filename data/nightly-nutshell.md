**2 new nightly failures: an AudienceGroup undelete assertion and a QuotaGroup QA 502 — no build changes to blame.**

_Likely cause: no build or QA-deploy changes in the window; new fails split into infra (QuotaGroup QA 502) and test/data (AudienceGroup undelete assertion)._

- AudienceGroup undelete assertion (test/data) + QuotaGroup QA 502 (infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9546121)
