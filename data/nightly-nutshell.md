**76 new failures — all server-side HTTP 500s from the QA product, pointing to a broken QA deployment, not the tests**

_Likely cause: QA-side 500s dominated by java.lang.AbstractMethodError (binary/dependency mismatch) plus NPE/IOOB and clone ValidationExceptions; no code changes recorded, so nothing to attribute._

- 31× server 500 → java.lang.AbstractMethodError on partnerEvents/quota endpoints (binary mismatch)
- 14× clone ValidationException + 14× 404 NOT_FOUND cascading from the same broken flows

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9409083)
