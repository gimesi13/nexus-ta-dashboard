**17 continuing failures, 0 new — QA parameter-service HTTP 500s plus 6 query-filter test assertions.**

_Likely cause: QA parameter-service.st-qa returning HTTP 500 on parameter search/categories (11 fails) plus 6 query-filter test assertions; no code or QA-deploy changes in the window to blame._

- 11× HTTP 500 from QA parameter-service (/parameters/search + /categories)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9621141)
