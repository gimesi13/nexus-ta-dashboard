**2 continuing failures in Communication rule validation — no new failures**

_Likely cause: stale negative-validation tests expecting an exception the API no longer throws; no new or infra failures._

- 2× Communication negative-validation assertions — expected exception not thrown (continuing, not infra).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9631958)
