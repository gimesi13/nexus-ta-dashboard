**3 new QuotaGroup failures from country/language support data — not infra, not a code change.**

_Likely cause: QA/SA/BY country-language combos the tests assume are enabled are rejected by the QA API (400 "Unsupported country"); no build changes and no timeouts, so test/reference-data drift._

- QA & BY rejected as "Unsupported country" (400); SA + [ar, en] rejected as unsupported combo
- No code changes and no infra timeouts — no commit or developer to blame

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9416344)
