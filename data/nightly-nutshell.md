**6 continuing failure(s) — no new unmuted fails**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 3× other — java.lang.RuntimeException:Project accept failed [sourceProjectId=<id>] [salesOrderGuid=abad79b4-4a6d-ef11-94b

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- GET /u1/bos/salesOrders/extended :: Response status 500 not defined for path '/u1/bos/salesOrders/extended'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9590350)
