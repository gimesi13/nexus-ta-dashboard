**9 new failures — mainly QuotaGroup, Quota**

_Likely cause: Possibly NXS-13489 by gergely.gimesi — touches QuotaGroup (8 overlapping new fails)._

- 6× assertion Condition not satisfied
- 2× other — Sell amount is lockable only when there are at least one sold quota which is greater than its quota capped val

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9543841)
