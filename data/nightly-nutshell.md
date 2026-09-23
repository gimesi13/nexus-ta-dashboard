**4 new failures — mainly Project**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 3× API ValidationException — jakarta.validation.ValidationException:Update failed, proposedStartDate must be before proposedEndDate. [proje
- 1× assertion Condition not satisfied

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- PUT /u1/nexus/projects/{}/dates/proposedEndDate :: Response status 500 not defined for path '/u1/nexus/projects/{projectId}/dates/proposedEndDate'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9539705)
