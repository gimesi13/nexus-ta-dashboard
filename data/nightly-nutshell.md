**16 new failures — a cluster of 15 QuotaGroup FIFO notification timeouts pointing at the fresh QuotaGroup QA deploys**

_Likely cause: QuotaGroup FIFO notifications never published — suspected QuotaGroup QA deploys NXS-14423 / NXS-14424 and NexusApi NXS-14422 (no per-commit author in evidence, so none named)._

- 15× PES2 notifications never published on the QuotaGroup FIFO topic within 90s — a pipeline regression, not a socket/502
- Separate lanes: 1× QA 502 (infra) and 4 new contract-drift endpoints

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9687623)
