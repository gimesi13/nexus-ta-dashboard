**4 new failures — mainly BOS, AudienceGroup**

_Likely cause: VCS changes present but none map onto the failing packages — likely test/data, correlate manually._

- 3× other — Project accept status is FINISHED. [projectId=<id>] [salesOrderGuid=abad79b4-4a6d-ef11-94bd-1253f55c3e9d]
- 1× QA 502 Bad Gateway

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- POST /u1/nexus/projects/{}/accept :: Response status 417 not defined for path '/u1/nexus/projects/{projectId}/accept'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9581994)
