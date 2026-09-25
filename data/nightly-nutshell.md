**9 new failures — all newly-added QuotaGroup scheduling tests (NXS-13489, gergely.gimesi) plus one Quota lock timing flake; no product regression**

_Likely cause: Newly-added NXS-13489 scheduling tests by gergely.gimesi are red on their first run (new coverage, some expected-red vs known bugs NXS-13937/13938/13939) — not infra, not a product regression._

- 8/9 new fails are in gimesi's new QuotaGroupScheduling* tests; labels mislead ('QA 504' is really an HTTP 500 expected-400 from quota-group-rest)
- 1 Quota lock failure is a separate cross-service lag (30s) flake

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9543841)
