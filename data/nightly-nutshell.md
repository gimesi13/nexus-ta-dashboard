**1 new Quota failure: feasibilityDistribution rejected with HTTP 400 (not infra)**

_Likely cause: test/data — HTTP 400 BAD_REQUEST "Invalid Quota setup or missing Feasibility Calculation!" on feasibilityDistribution; no source changes to blame._

- Quota / SoldQuotaWorkflowTestSteps — RuntimeException from HTTP 400 on feasibilityDistribution (not a timeout/502/504)
- No build changes recorded — no commit or developer to attribute

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9433205)
