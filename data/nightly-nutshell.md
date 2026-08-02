**Build failed: 5 continuing failures, no new regressions — QA infra timeouts + QuotaGroup country/language test-data mismatches**

_Likely cause: mixed — 2 ChangeOrderFlow tests hit QA d365/CRM socket timeouts (infra); 3 QuotaGroup tests are country/language validation/assertion mismatches (test/data). No build changes, so no commit implicated._

- 2× ChangeOrderFlow — java.net.SocketTimeoutException to QA d365/CRM (infra)
- 3× QuotaGroup — QA/SA/BY country-language validation/assertion mismatch (test/data)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9419943)
