**2 new failures in Quota**

_Likely cause: Possibly NXS-13674 by gergely.gimesi — touches Quota, QuotaGroup (2 overlapping new fails)._

- 1× QA 504 timeout — Sell amount is lockable only when there are at least one sold quota which is greater than its quota capped val

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9469413)
