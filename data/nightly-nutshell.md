**2 new failures in Fieldwork**

_Likely cause: VCS changes present but none map onto the failing packages — likely test/data, correlate manually._

- 1× other — feign.RetryableException:microservices-qa.dynata.com executing GET <url> Caused by: java.net.UnknownHostExcept

⚠️ Contract drift: 5 new response-schema violation(s) vs baseline.
- GET /u1/meta/countries :: No API path found that matches request '/u1/meta/countries'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9690523)
