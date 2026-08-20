**1 new QuotaGroup failure from a QA socket timeout on the D365 changeOrderStatus endpoint — infra, not a code regression.**

_Likely cause: QA/infra socket timeout (java.net.SocketTimeoutException) on POST d365/changeOrderStatus, not a code regression._

- 1× QuotaGroup — Feign SocketTimeoutException on POST d365/changeOrderStatus (500 wrapping a client timeout).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9482712)
