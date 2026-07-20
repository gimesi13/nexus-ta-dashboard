**43 new failures — mostly QA infra timeouts/502s**

_Likely cause: QA infrastructure (502/504/read timeouts; dk-project-feasibility-data-store, dk-project-quota-details-rest) — not a code regression._

- 41× QA 502 Bad Gateway
- 1× Settings defaultCountries lag

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9400525)
