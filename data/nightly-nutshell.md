**22 new Parameter failures from one QA dependency outage — dk-management-feature-rest was unreachable (feign.RetryableException).**

_Likely cause: QA infra — dk-project-target-editor-rest got a feign.RetryableException calling dk-management-feature-rest, cascading 500s through NexusApi qualificationPaths; no deployed code change maps to the failing dependency._

- 22× identical feign.RetryableException to dk-management-feature-rest:8080 → cascading 500s in NexusApi qualificationPaths

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9700789)
