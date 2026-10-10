**16 new failures — mainly Survey**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 16× other — (no error message)

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- GET /u1/bos/salesOrders/extended :: Response status 500 not defined for path '/u1/bos/salesOrders/extended'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9608929)
