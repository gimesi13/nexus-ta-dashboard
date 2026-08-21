**1 new PartnerEvent failure — a server-side NPE (HTTP 500) on POST /partnerEvents, not infra or a test flake.**

_Likely cause: server-side NullPointerException (500) on POST /partnerEvents ("currencyCode" from a null "qgPrice") — a product bug, but no code changes were deployed this window, so no commit can be named._

- NEW · PartnerEvent — server 500 NPE: Cannot read field 'currencyCode' because 'qgPrice' is null (product bug, not a timeout).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9483809)
