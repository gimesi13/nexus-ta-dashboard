**1 new Quota failure — a backend HTTP 400 on the feasibility path, not the labeled QA 504 timeout**

_Likely cause: a backend HTTP 400 BAD_REQUEST from dk-project-details-editor-rest's feasibilityDistribution — not a QA 504 timeout and not from any test-module commit; correlate against in-window QA deploys._

- 1× Quota — HTTP 400 BAD_REQUEST from dk-project-details-editor-rest /feasibilityDistribution (not a 504 timeout)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9471118)
