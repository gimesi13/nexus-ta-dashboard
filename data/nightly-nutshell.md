**1 new failure in Segment — a transient QA 502 Bad Gateway (infra).**

_Likely cause: QA 502 Bad Gateway on PUT /u1/nexus/quotaGroups — transient infra, not a product regression._

- 1× QA 502 Bad Gateway (Segment initializationError, new)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9587614)
