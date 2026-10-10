**16 new Survey failures — all HTTP 500 from the allocation-engine url-service (/v1/urlPatterns/test/resolve) during survey test-link generation.**

_Likely cause: backend regression in the allocation-engine url-service (POST /v1/urlPatterns/test/resolve returns 500) — not a QA timeout/502/504 flake; no QA-deploy commit touches url-service, so no developer is blamed._

- 16 new Survey fails share one signature: url-service → HTTP 500 via dk-project-survey-rest → NexusApi /u1/nexus/surveys/{}/tests
- Deterministic 500 (not timeout/502/504) → backend regression, not this test module

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9608929)
