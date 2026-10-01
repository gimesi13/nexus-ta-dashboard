**4 new failures, all server-side errors: a QA 502 in AudienceGroup plus a 3-test BOS project-accept cluster (500/417) — no code change implicated.**

_Likely cause: QA backend/infra instability in the deploy window — a 502 and backend 500/417 on project-accept, with no TA-module or deployed-service change mapping to the failing path._

- 3× BOS sample creation — POST /projects/{id}/accept returns 500/417 for one salesOrderGuid (DkmsError, cloneQuotaGroup ParallelError)
- AudienceGroup E2E — QA 502 Bad Gateway on fullAudienceGroupSetup = infra

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9581994)
