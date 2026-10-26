**2 continuing Communication negative-validation failures — no new failures**

_Likely cause: stale test/data — Communication negative tests expected an exception that is no longer thrown; no code changes in the window._

- 2× stale negative validation in Communication (contract drift separately flagged `GET /u1/meta/countries`)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9634904)
