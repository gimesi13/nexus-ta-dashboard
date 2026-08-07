**No new failures — the one continuing failure is a QA socket timeout (infra), not a code regression.**

_Likely cause: infra — a Feign 'Read timed out' on a QuotaGroup DELETE against microservices-qa; no TA commit or QA backend deploy maps to it._

- 0 new failures; 1 continuing infra timeout
- QuotaGroup: Feign 'Read timed out' on DELETE audienceGroups — client/socket timeout

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9446824)
