**1 new Fieldwork failure: delivery mode returned STANDARD instead of the expected ACCELERATED.**

_Likely cause: real assertion (not infra) — delivery mode was STANDARD, not ACCELERATED; no changed file maps cleanly to delivery-mode logic, so test/data is the leading suspect._

- Fieldwork: delivery3.deliveryMode STANDARD vs expected ACCELERATED (assertion, not infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9530571)
