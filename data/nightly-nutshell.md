**6 new failures — mainly QuotaGroup, BOS**

_Likely cause: Possibly NXS-13848 by gergely.gimesi — touches QuotaGroup (5 overlapping new fails)._

- 3× other — java.lang.RuntimeException: Timeout after waiting 187 seconds: Condition never returned a non-null result
- 2× QA 502 Bad Gateway

⚠️ Contract drift: 3 new response-schema violation(s) vs baseline.
- GET /u1/nexus/urlPools/{} :: Response status 500 not defined for path '/u1/nexus/urlPools/{urlPoolId}'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9578565)
