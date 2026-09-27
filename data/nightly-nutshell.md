**11 continuing failure(s) — no new unmuted fails**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 6× other — java.lang.IllegalStateException:Audience cannot be started due to missing lineItemGuid. [quotaGroupId=<id>]

⚠️ Contract drift: 1 new response-schema violation(s) vs baseline.
- POST /u1/nexus/quotaGroups/{}/core/changeStatus :: Response status 500 not defined for path '/u1/nexus/quotaGroups/{quotaGroupId}/core/changeStatus'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9545381)
