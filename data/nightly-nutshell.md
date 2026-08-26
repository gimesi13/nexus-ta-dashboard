**1 continuing failure — a QA Feign socket timeout; no new failures this run.**

_Likely cause: QA socket timeout (infra) — Feign 'Read timed out' calling dk-project-crm-rest changeOrderStatus, not a code regression._

- 1× client/Feign socket timeout — Read timed out POST /api/Crm/u1/test/changeOrderStatus (dk-project-crm-rest)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9490612)
