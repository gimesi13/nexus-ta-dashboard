**2 new failures (AudienceGroup, Fieldwork) — assertions/timing, not infra**

_Likely cause: no test-module changes and QA-deployed commits don't touch these areas — test/data or read-after-write timing flakiness._

- AudienceGroup — undelete PUT succeeded but GET still isDeleted=true after 15s (read-after-write convergence)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9522717)
