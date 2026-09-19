**15 PES notification tests time out waiting for QuotaGroup FIFO events — points to QA deploy NXS-13893 (ProjectEventForwarder messaging).**

_Likely cause: QA deploy NXS-13893 "fix Instant type in headers" (norbert.farkas) changed ProjectEventForwarder's ActiveMQ messaging path; the PES2 FIFO notifications never publish, so 15 tests time out._

- 15× PES — 90s timeout in waitForPes2Notification; QuotaGroup FIFO event never published (missing message, not a socket/502)
- 1× Quota — sold-quota lock fails on cross-service feasibility lag; separate, likely test/data

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9533976)
