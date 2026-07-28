**1 new QuotaGroup failure — a QA socket timeout (infra), not a code change.**

_Likely cause: Feign SocketTimeoutException to microservices-qa (QA infra); no build changes, so no commit implicated._

- NEW: QuotaGroup change order flow — SocketTimeoutException to microservices-qa (infra).
- 3 older failures unrelated (assertion, read-timeout, PES tally data).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9412090)
