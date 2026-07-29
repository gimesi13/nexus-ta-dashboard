**Nightly is effectively green — 0 new failures; the only failure is a continuing change-order approval timeout, not a regression.**

_Likely cause: infra — a QA timeout (WaitUtil waited 45s for change-order approval, "Condition never returned a non-null result"); continuing, not new, so no code blame._

- 0 new failures; only failure is change-order approve timing out after 45s (QA timing, not an assertion).
- NXS-13505 (gergely.gimesi) was a change-order wait fix; failures dropped 4→1.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9414999)
