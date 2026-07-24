**Nightly build broke at compilation — :compileJava failed, so no tests ran.**

_Likely cause: code change NXS-13454 by gergely.gimesi edited Java Feign clients under src/main/java; not infra._

- Build failed at :compileJava (new) — 0 tests ran
- Suspect: NXS-13454 (gergely.gimesi) — Java Feign client edits

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9409020)
