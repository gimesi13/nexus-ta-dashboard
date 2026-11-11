**3 new Communication topic failures from new quota-group-language validation (NXS-14273)**

_Likely cause: Code change — NXS-14273 (tamasroma) made the topics endpoints require quota group languages; 400 BAD_REQUEST, not infra._

- 3× Communication — 400 BAD_REQUEST on PUT /communicationTopics: topic language must be a quota group language

⚠️ Contract drift: 4 new response-schema violation(s) vs baseline.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9674096)
