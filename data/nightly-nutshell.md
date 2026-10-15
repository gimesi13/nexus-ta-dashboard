**1 new failure in SampleRules**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× QA 502 Bad Gateway

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- POST /u1/nexus/quotaGroups :: Response status 502 not defined for path '/u1/nexus/quotaGroups'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9617673)
