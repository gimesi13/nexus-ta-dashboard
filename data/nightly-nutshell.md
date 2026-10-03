**2 new non-infra failures (AudienceGroup undelete assertion, Quota lock cross-service lag) — no deployed backend change maps to either area.**

_Likely cause: test/data or QA environment flakiness — no deployed backend change touches AudienceGroup or Quota._

- AudienceGroup undelete assertion (isDeleted still true) + Quota sold-quota lock timeout after 30s cross-service lag

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9590056)
