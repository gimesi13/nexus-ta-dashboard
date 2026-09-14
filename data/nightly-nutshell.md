**1 new failure in Quota**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× other — Sell amount is lockable only when there are at least one sold quota which is greater than its quota capped val

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- GET /u1/nexus/urlPools/{} :: Response status 500 not defined for path '/u1/nexus/urlPools/{urlPoolId}'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9522779)
