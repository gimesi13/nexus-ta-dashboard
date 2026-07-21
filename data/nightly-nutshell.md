**No new failures — 1 continuing QuotaGroup test/data failure (GB + [en, fr] unsupported)**

_Likely cause: test/data — the QuotaGroup E2E test posts an unsupported GB + [en, fr] combo and gets a clean HTTP 400; not infra, not a code change (this run's changes only touch dashboard/docs/automation)._

- 0 new failures; 1 continuing (QuotaGroup E2E)
- GB + [en, fr] unsupported — clean HTTP 400 BAD_REQUEST; fix test data (use a multi-language market such as CA)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9402753)
