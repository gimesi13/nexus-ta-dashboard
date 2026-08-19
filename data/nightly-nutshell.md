**1 new Quota failure — a feasibility HTTP 400, not the labeled 504 timeout**

_Likely cause: test/data — a single feasibility request was rejected (HTTP 400 "Feasibility Calculation unavailable!"); no code change or QA deploy maps to it._

- Quota / SoldQuotaLockUnlock "Adding parameters…triggers feasibility": HTTP 400 from dk-project-details-editor-rest; sibling scenarios passed.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9479427)
