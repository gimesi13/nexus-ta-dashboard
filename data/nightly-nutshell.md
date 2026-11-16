**2 new failures: a QuotaGroup scheduling timeout and a Survey URL-upload assertion**

_Likely cause: QuotaGroup scheduling timeout plausibly from NXS-13904 (david.nagy) QG mongo→feign refactor; Survey assertion unmatched (test/data)._

- QuotaGroup: waitForScheduleToRun timed out after 90s; Survey upload returned uploaded=0

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9684995)
