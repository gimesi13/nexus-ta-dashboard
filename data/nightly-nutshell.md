**2 new Fieldwork soft-launch failures, both QA backend 500s from a feign DNS error**

_Likely cause: QA DNS/network — ThrottlingSetting returns 500 driven by feign.RetryableException / java.net.UnknownHostException to microservices-qa.dynata.com, not a code regression._

- 2× Fieldwork soft-launch — HTTP 500 PUT softLaunchQuota, root cause feign / UnknownHostException (QA DNS)

⚠️ Contract drift (separate lane): 5 new response-schema violation(s) vs baseline.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9690523)
