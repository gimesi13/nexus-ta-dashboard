**22 new failures — mainly Parameter**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 22× other — feign.RetryableException:dk-management-feature-rest.nexus-ms-qa.dynata.com executing GET <url> Caused by: java

⚠️ Contract drift: 6 new response-schema violation(s) vs baseline.
- PATCH /u1/nexus/projects/{}/endlinkSecurity 500 :: Response status 500 not defined for path '/u1/nexus/projects/{projectId}/endlinkSecurity'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9700789)
