**2 new failures — a real backend HTTP 500 in QuotaGroupRest plus a Quota test-helper timeout (not the infra 504 the cluster label suggests).**

_Likely cause: mixed — a genuine backend HTTP 500 IndexOutOfBoundsException from dk-project-quota-group-rest (product bug), plus a test-helper timeout at QuotaGroupHelper.groovy:810 touched by NXS-13674 (gergely.gimesi)._

- QuotaGroup: HTTP 500 IndexOutOfBoundsException from dk-project-quota-group-rest on DELETE quotaGroups — backend bug (QA deploy NXS-13682 was CloudFormation-only).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9469413)
