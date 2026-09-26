**5 new failures — mainly QuotaGroup**

_Likely cause: Possibly NXS-13489 by gergely.gimesi — touches QuotaGroup (5 overlapping new fails)._

- 5× other — java.lang.IllegalStateException:Audience cannot be started due to missing lineItemGuid. [quotaGroupId=<id>]
- Change NXS-13489: gergely.gimesi · QuotaGroup · 5 overlapping new fails

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- GET /u1/nexus/urlPools/{} :: Response status 500 not defined for path '/u1/nexus/urlPools/{urlPoolId}'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9545174)
