**1 new QuotaGroup failure — a transient backend 500 (ConcurrentModificationException), not attributable to any QA deploy.**

_Likely cause: transient backend 500 (ConcurrentModificationException) on POST /u1/nexus/quotaGroups; no QA-deploy change maps to the quota-group service._

- QuotaGroup initializationError — HTTP 500 ConcurrentModificationException on quota-group-rest createInProgress.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9601454)
