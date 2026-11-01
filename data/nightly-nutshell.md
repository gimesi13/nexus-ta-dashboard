**4 continuing failure(s) — no new unmuted fails**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 2× server NestedServletException / NPE — java.lang.NullPointerException:Cannot assign field \

⚠️ Contract drift: 5 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9650456)
