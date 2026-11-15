**2 new failures in QuotaGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× other — java.lang.RuntimeException: Timeout after waiting 90 seconds: Condition never returned a non-null result

⚠️ Contract drift: 4 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9683759)
