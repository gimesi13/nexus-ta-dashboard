**2 new failures in QuotaGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 2× client/Feign socket timeout — feign.RetryableException:timeout executing POST <url> Caused by: java.net.SocketTimeoutException:timeout

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9419476)
