**1 new Quota failure — a 20s cross-service propagation timeout, with no code changes in the window.**

_Likely cause: environment/timing flakiness — a 20s cross-service propagation lag (QuotaDetails→DetailsEditor); no code changes in the window to blame._

- 1× Quota: sold-quota lock timed out after 20s on propagation lag — a wait-timeout, not an assertion

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9522779)
