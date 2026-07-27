**2 new failures in QuotaGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× client/Feign socket timeout — feign.RetryableException: Read timed out executing DELETE <url>
- 1× NOT_FOUND / missing data — java.lang.reflect.UndeclaredThrowableException:java.lang.reflect.UndeclaredThrowableException Caused by: java.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9410783)
