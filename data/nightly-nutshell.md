**1 new Quota failure from a QA data-setup error (setMockData 500), no code change implicated.**

_Likely cause: QA data-setup issue — setMockData on feasibility-data-store returned 500 (inner 400 from details-editor); no TA change or QA deploy maps to those endpoints._

- Quota/SoldQuotaValidationTestSteps failed in setup before any assertion — not a timeout/502/504 and not a product regression we can pin.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9450738)
