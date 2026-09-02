**1 new failure in Fieldwork**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 1× QA 502 Bad Gateway

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- PUT /u1/nexus/quotaGroups/{}/conditions/segmentedConditions/{} :: Response status 502 not defined for path '/u1/nexus/quotaGroups/{quotaGroupId}/conditions/segmentedConditions/{parameterId}'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9503948)
