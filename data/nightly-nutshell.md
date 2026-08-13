**1 new assertion failure in BOS (D365 sample creation)**

_Likely cause: a Spock assertion on clonedFromQuotaGroupId (118749158 vs expected 118749154) — no changed file maps to BOS, likely test/data._

- 1× assertion 'Condition not satisfied' in BOS D365 sample creation

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9463899)
