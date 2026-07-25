**1 new failure in QuotaGroup change-order flow - an assertion, not infra.**

_Likely cause: test-data/response-shape - QuotaGroup ChangeOrderFlow assertion (isChangeOrderNeeded expected true, but AudienceChangeStatus came back all-null); no VCS change maps to QuotaGroup._

- New: QuotaGroup ChangeOrderFlow assertion `isChangeOrderNeeded == true` failed (returned null)
- Not infra - no timeout/502/504 on the new failure

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9410446)
