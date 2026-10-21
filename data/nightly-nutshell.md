**3 new failures in Communication**

_Likely cause: Possibly NXS-14188 by gergely.gimesi — touches Communication (2 overlapping new fails)._

- 2× stale negative validation — Expected exception of type 'java.lang.Exception', but no exception was thrown

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9628628)
