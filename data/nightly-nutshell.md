**2 new Survey failures are a QA MongoDB authorization outage, not a code regression.**

_Likely cause: QA infra — the test-link microservice returns HTTP 500 because MongoDB rejects error 13 'Authorization failure' on nexus-api-mongo-qa._

- 2× Survey (SurveyCRUDTestSteps) test-link endpoints return HTTP 500 from QA
- No code blame — regression-suite changes cannot cause a server-side Mongo auth failure

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9438931)
