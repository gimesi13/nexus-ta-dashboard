**5 new failures in Project overview and Survey — all NOT_FOUND for missing ProjectProperties in QA.**

_Likely cause: missing QA test data/environment — no build changes and no timeouts/502/504, so not a code regression or infra outage._

- 4× Project overview — 404 "Could not find ProjectProperties 11947ce3…" on project 2183035
- 1× Survey deactivate — 404 "Could not find ProjectProperties 63d4049d…"

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9417182)
