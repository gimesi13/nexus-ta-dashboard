**1 new failure in Quota — QA 502 Bad Gateway (infra), not a product regression.**

_Likely cause: QA infrastructure — a transient 502 Bad Gateway from dk-project-quota-details-rest; no build changes, so no commit to blame._

- 1× new: Quota 502 Bad Gateway (infra)
- No build changes — no commit to blame

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9420645)
