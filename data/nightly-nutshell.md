**1 new failure in Quota is a QA 502 Bad Gateway — infra, not a product regression.**

_Likely cause: QA gateway 502 hitting dk-project-quota-details-rest; no code changes shipped, so no commit to blame._

- 1× new: QA 502 Bad Gateway (Quota) — infra
- No code changes in this build

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9420645)
