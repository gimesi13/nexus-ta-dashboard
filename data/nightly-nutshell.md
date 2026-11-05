**13 continuing failures (0 new) — all are server-side 500 NullPointerExceptions from Survey REST's urlPools path, not QA infra.**

_Likely cause: continuing server-side 500 NPEs from dk-project-survey-rest on the urlPools delete/activate path (a product bug, not QA infra); no in-window QA deploy touches that service, so no commit is pinned._

- 13 continuing fails, 0 new — identical 500 NullPointerException (List.isEmpty() on null) from dk-project-survey-rest on /urlPools

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9661775)
