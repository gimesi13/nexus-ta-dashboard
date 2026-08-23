**1 continuing failure — a QA socket timeout, no new unmuted fails**

_Likely cause: QA infra — a Feign/socket timeout on changeOrderStatus, not a code change._

- 1× QuotaGroup — Feign SocketTimeout on POST changeOrderStatus (QA infra timeout, continuing)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9484624)
