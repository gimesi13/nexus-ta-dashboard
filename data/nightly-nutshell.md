**15 continuing PES soft-launch notification timeouts — no new failures this run.**

_Likely cause: pre-existing PES soft-launch notification timeouts (environmental), not a code change._

- 15× PES soft-launch vs tally — 90s timeout waiting for QuotaGroup FIFO notifications (all continuing, none new).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9536486)
