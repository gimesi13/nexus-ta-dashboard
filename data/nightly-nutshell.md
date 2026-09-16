**1 new failure in Quota**

_Likely cause: soldQuota feasibility wait-timeout (async, not infra) — likely QuotaGroupRest change NXS-13879 by david.nagy._

- 1× Quota — soldQuota feasibility wait timed out after 30s (Condition never returned a non-null result), not a socket/502 infra timeout

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9528284)
