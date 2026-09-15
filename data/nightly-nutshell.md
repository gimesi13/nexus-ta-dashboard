**1 new Quota failure: sold-quota lock timed out from cross-service propagation lag.**

_Likely cause: test/environment timing — DetailsEditor didn't register a sold quota above its capped value within the 20s lock window (propagation lag with QuotaDetails); no QA-deployed service touches Quota code._

- Quota: sold-quota lock timed out after 20s (QuotaDetails→DetailsEditor propagation lag).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9525464)
