**2 new failures in AudienceGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× assertion Condition not satisfied

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- POST /u1/nexus/quotaGroups :: Response status 502 not defined for path '/u1/nexus/quotaGroups'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9546121)
