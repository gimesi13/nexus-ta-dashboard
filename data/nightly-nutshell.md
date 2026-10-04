**6 continuing failures (0 new) — QA backend 500s in BOS and QuotaGroup, no code changes in the window.**

_Likely cause: QA backend 500s (BOS project-accept, QuotaGroup saveDatesAndSchedules) plus a PartnerEvent 404 — all continuing, no commits in the window to blame._

- BOS 3× & QuotaGroup 2×: QA backend returns 500 where a normal response / 400 was expected.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9590350)
