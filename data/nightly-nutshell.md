**3 new failures are mostly QA infra plus one PES soft-launch data issue — no code regression confirmed.**

_Likely cause: mixed — a 120s read timeout on audienceGroups/clone and a 500 from QA feasibility-data-store (infra), plus a PES soft-launch vs tally fixture issue (test-data)._

- QuotaGroup 'Move quota group…' — Read timed out after 120s (infra); Quota 'Modifying totalQuota…' — HTTP 500 from QA feasibility-data-store (backend/env)
- pes 'tally mode update…' — HTTP 400 'total quota less than soft launch quota' (test-data fixture)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9406176)
