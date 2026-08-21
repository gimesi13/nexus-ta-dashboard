**1 new failure in PartnerEvent**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× server NestedServletException / NPE — java.lang.NullPointerException:Cannot read field \

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- POST /u1/nexus/partnerEvents :: Response status 500 not defined for path '/u1/nexus/partnerEvents'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9483809)
