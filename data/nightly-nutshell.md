**3 new failures in QuotaGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 2× GB + fr unsupported — Unsupported country-language combinations! [countryIso:SA] [languageIsos:[ar, en]]
- 1× other — Unsupported country! [countryIso:QA]

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9416344)
