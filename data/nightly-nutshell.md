**9 new failures — mostly QA infra timeouts/502s**

_Likely cause: QA infrastructure (502/504/read timeouts; dk-project-communication-rest) — not a code regression._

- 6× client/Feign socket timeout — feign.RetryableException: Read timed out executing POST <url>

⚠️ Contract drift: 5 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9643033)
