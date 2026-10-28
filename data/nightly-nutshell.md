**5 continuing failures and no new fails — four Lookup optionAssembler 400s and one stale validation test, none infra.**

_Likely cause: No new failures or tonight code change — Lookup 400 'selectionMode must not be null' request-validation errors plus a stale negative-validation test, not infra._

- 4× Lookup — optionAssembler returns 400 'selectionMode must not be null' (request validation, not a QA timeout/502/504)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9640551)
