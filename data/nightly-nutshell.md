**15 continuing PES2-notification timeouts — no new failures this run.**

_Likely cause: No test-module or QA-deploy changes in the window; the 15 PES2 FIFO-notification timeouts are all continuing failures pointing to test/data or messaging-environment flakiness._

- 15× PES2 QuotaGroup FIFO notification waits timed out at 90s — all continuing, 0 new

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9535379)
