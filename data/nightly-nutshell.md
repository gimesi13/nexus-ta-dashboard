**2 new product-behavior assertion failures in Fieldwork and QuotaGroup scheduling (not infra)**

_Likely cause: QuotaGroup scheduled Start never ran and Fieldwork delivery mode stayed SLOWEST; leading suspect is the QA-deployed QuotaGroupRest Field-Schedule SSE change (NXS-13987), unconfirmed._

- QuotaGroup scheduled Start timed out after 84s; Fieldwork delivery mode expected ACCELERATED, got SLOWEST

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9614812)
