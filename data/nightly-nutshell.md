**1 continuing Feign socket timeout — no new failures, likely QA infra**

_Likely cause: QA infra — Feign SocketTimeout to d365/changeOrderStatus, not a code regression._

- 1× QuotaGroup change-order flow — Feign/client socket timeout (infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9487993)
