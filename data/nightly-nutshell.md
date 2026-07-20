**43 new failures — almost all QA infra (502/504), no code changes**

_Likely cause: QA infrastructure — 502/504 from the QA gateway (dk-project-feasibility-data-store, dk-project-quota-details-rest); no VCS changes, so not a code regression._

- 42 of 43 new failures are QA infra (41× 502, 1× 504)
- 1× Settings defaultCountries assertion (read-after-write flake)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9400525)
