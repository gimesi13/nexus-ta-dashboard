**2 new failures — a QuotaGroup QA socket timeout and a flaky Settings default-countries assertion; no code change implicated.**

_Likely cause: mixed — infra (QA d365 socket timeout) plus a flaky Settings read-after-write assertion; no commit blamed._

- QuotaGroup ChangeOrderFlow — feign SocketTimeoutException / 500 from QA d365 changeOrderStatus (infra)
- Settings Set default countries — expected [US, GB, CA] but got [HU, AU] (flaky read-after-write)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9404850)
