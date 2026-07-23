**3 new failures in Quota**

_Likely cause: Possibly NXS-13454 by gergely.gimesi — touches Quota, QuotaGroup (2 overlapping new fails)._

- 2× other — java.lang.RuntimeException: <url>
- 1× PES soft-launch vs tally — Tally mode change is not allowed, because total quota less than soft launch quota!

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9406176)
