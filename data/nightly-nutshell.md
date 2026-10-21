**3 new failures: 2 Communication negative-validation tests + 1 QuotaGroup QA 502**

_Likely cause: mixed — the 2 Communication fails are a test-coverage change in CommunicationRuleValidationTestSteps (NXS-14188, gergely.gimesi); the QuotaGroup fail is a QA 502 (infra)._

- 2× Communication "expected exception not thrown" (NXS-14188 test change) · 1× QuotaGroup 502 (infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9628628)
