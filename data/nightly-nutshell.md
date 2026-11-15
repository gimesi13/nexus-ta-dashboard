**2 new QuotaGroup failures — both a 90s scheduler-execution timeout, not a code change**

_Likely cause: QA scheduling/environment slowness — `waitForScheduleToRun` times out after 90s; no commits landed in this test module or the QA deploy window._

- Both new fails (scheduled STOP and START) share one root; the 'Condition not satisfied' one is that same timeout wrapped in a Spock check, not a real assertion.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9683759)
