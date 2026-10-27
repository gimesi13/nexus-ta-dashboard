**5 new failures — mainly Lookup, Quota**

_Likely cause: VCS changes present but none map onto the failing packages — likely test/data, correlate manually._

- 5× other — selectionMode must not be null

⚠️ Contract drift: 5 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9637155)
