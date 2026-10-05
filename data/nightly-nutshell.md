**2 new failures in Project**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 2× other — groovy.lang.MissingMethodException: No signature of method: com.dynata.rest.gateway.nexusapi.rest.tests.helper

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- GET /u1/bos/salesOrders/extended :: Response status 500 not defined for path '/u1/bos/salesOrders/extended'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9590724)
