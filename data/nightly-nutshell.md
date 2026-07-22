**2 new failures, no code changes in this build: a ~60s QuotaGroup timeout (infra-looking) plus a fast-failing Settings test.**

_Likely cause: mixed — QuotaGroup timed out at ~60s (infra/QA), Settings failed in 190ms (likely test/data); no code changes shipped, so no commit is blamed._

- QuotaGroup · change order flow — ~60s runtime = timeout/infra signature
- Settings · Set default countries — 190ms fast fail, likely assertion/test-data

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9404850)
