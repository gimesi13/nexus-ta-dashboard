**17 new failures in Parameter/Segment — downstream parameter-service returning HTTP 500, plus a test-assertion bug**

_Likely cause: mixed — downstream parameter-service 500s (not infra) plus a broken test assertion; no in-window QA deploy touches parameter-service._

- 11× HTTP 500 from downstream parameter-service (`/parameters/search`, `/search/categories`) — backend error, not infra
- 6× test-assertion bug (`query.contains('!@#')` at ParameterSearchFiltersAndConditionsTestSteps.groovy:47); contract drift: POST /parameters/search 500 not in contract

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9619919)
