**2 new failures in QuotaGroup**

_Likely cause: Possibly NXS-14576 by gergely.gimesi — touches Segment (1 overlapping new fails)._

- 2× assertion Condition not satisfied

⚠️ Contract drift: 3 new response-schema violation(s) vs baseline.
- PATCH /u1/nexus/projects/{}/endlinkSecurity 500 :: Response status 500 not defined for path '/u1/nexus/projects/{projectId}/endlinkSecurity'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9703643)
