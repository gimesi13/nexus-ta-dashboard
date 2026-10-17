**17 new failures — mainly Parameter, Segment**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 9× other — (no error message)
- 8× assertion Condition not satisfied — (no error message)

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- POST /u1/nexus/parameters/search :: Response status 500 not defined for path '/u1/nexus/parameters/search'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9619919)
