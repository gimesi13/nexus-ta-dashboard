**11 new failures — mainly Fieldwork**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 11× other — Update failed. softLaunchStartDate must not be in the past. [value=Fri Oct 31 20:00:00 EDT 2025]

⚠️ Contract drift: 3 new response-schema violation(s) vs baseline.
- GET /u1/bos/salesOrders/extended :: Response status 500 not defined for path '/u1/bos/salesOrders/extended'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9609001)
