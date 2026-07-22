**2 new failures in QuotaGroup**

_Likely cause: Possibly NXS-13444 by gergely.gimesi — touches QuotaGroup (1 overlapping new fails)._

- 1× client/Feign socket timeout — feign.RetryableException:timeout executing POST <url> Caused by: java.net.SocketTimeoutException:timeout
- 1× Settings defaultCountries lag

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9404850)
