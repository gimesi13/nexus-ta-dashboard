**5 new failures — 3 QA read-timeouts on Project/fullProjectSetup, plus one Communication assertion likely from the CommunicationRest refactor**

_Likely cause: mostly QA Feign read-timeouts, but the new Communication assertion maps to gyarmatitamas's communication refactor (NXS-14418 / NXS-14454)._

- Communication: 400 "Communication is not supported for this project" — NXS-14418 / NXS-14454 (gyarmatitamas)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9689412)
