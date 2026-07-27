**2 new failures, both QA-environment errors during test setup — not a code change.**

_Likely cause: QA environment instability — a Feign read timeout plus an HTTP 500 from a QA backend during setup; no source changes, so no commit implicated._

- QuotaGroup: Feign "Read timed out" on DELETE /audienceGroups (QA socket timeout)
- Survey: HTTP 500 from dk-project-target-editor-rest during setup (QA server error, not missing data)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9410783)
