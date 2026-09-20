**1 new Project E2E failure — 20s async quota-setup timeout, no code changes to blame.**

_Likely cause: No build or QA-deploy changes; a 20s WaitUtil timeout in setProjectTotalQuota, most likely async/environment flakiness._

- 1× Project E2E — WaitUtil timeout (20s) at ProjectHelper.setProjectTotalQuota, condition never returned

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9534498)
