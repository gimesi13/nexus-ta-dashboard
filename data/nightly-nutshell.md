**11 new Fieldwork soft-launch failures — newly deployed date validation is rejecting the tests' stale 2025 dates.**

_Likely cause: NXS-11709 (david.nagy) added soft-launch input validation; the Fieldwork tests still send 2025 dates now rejected as "in the past" — mixed code change + stale test data._

- 11× Fieldwork: 400 "softLaunchStartDate must not be in the past" at `/softLaunch/softLaunchDatesWithInterval` (dates in 2025)
- Contract drift (separate lane, 3 new): 500s on `/salesOrders/extended`, `/urlPools/{}`, `/surveys/{}/tests`

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9609001)
