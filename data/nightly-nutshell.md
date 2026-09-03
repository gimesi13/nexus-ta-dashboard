**4 new Settings failures from a QA MongoDB authorization error on dk-system-user-rest — infra, not a code change.**

_Likely cause: QA MongoDB 'Authorization failure' (error 13) on nexus-api-mongo-qa making dk-system-user-rest return 500 on /userSettings — infra, not a product code change._

- 4× Settings /userSettings calls → HTTP 500 from dk-system-user-rest (MongoDB error 13 auth failure).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9505988)
