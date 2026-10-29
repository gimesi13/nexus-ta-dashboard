**9 new failures — mostly QA Feign read-timeouts (infra), plus a Communication backend 500 and two assertion/validation fails.**

_Likely cause: 6 of 9 new fails are QA Feign read-timeouts (infra); the rest are a Communication backend 500 and two Quota/Communication assertion fails (one plausibly NXS-14256 / gergely.gimesi)._

- 6× Feign "Read timed out" (Project ×4, QuotaGroup ×2) — QA infra; 3 non-infra: Communication 500 + cancel-state assertion + Quota negative-validation

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9643033)
