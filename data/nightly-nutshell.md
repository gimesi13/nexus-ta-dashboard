**2 new QuotaGroup failures are QA CRM change-order timeouts, not a code regression.**

_Likely cause: QA infra — both new failures time out on POST to the QA CRM changeOrderStatus endpoint (SocketTimeout / Read timed out); no VCS changes this run._

- 2× new: change-order flow tests time out on POST to QA CRM (dk-project-crm-rest / d365 changeOrderStatus)
- No VCS changes this run — no code or developer to blame

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9419476)
