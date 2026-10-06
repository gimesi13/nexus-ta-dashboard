**1 new failure in AudienceGroup: undelete read-after-write didn't converge within 15 s.**

_Likely cause: AudienceGroup undelete PUT succeeded but GET still reported isDeleted=true after 15 s; no QA deploy touches AudienceGroup — likely test/data or environment timing._

- 1× AudienceGroup — undelete PUT succeeded but GET still isDeleted=true after 15 s

⚠️ Contract drift (separate lane): GET /u1/bos/salesOrders/extended returned 500 not defined in the OpenAPI contract (1 new vs baseline).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9598471)
