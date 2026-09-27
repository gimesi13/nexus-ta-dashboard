**11 continuing QuotaGroup failures (0 new) — backend 500s and assertion mismatches, no commits to blame.**

_Likely cause: mixed — QuotaGroup backend HTTP 500s on changeStatus/saveDates plus genuine assertion mismatches; no commits landed in the window to implicate._

- 6× changeStatus?START → HTTP 500 "missing lineItemGuid" (backend error, not a timeout)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9545381)
