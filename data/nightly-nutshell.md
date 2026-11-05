**13 new failures, all one server-side bug: SurveyRest returns HTTP 500 (NullPointerException) on /u1/urlPools, breaking PES, Fieldwork and Survey tests**

_Likely cause: SurveyRest deploy NA-2051 (adam.szotak) — dk-project-survey-rest throws a 500 NPE on /u1/urlPools; a product bug, not infra._

- 13/13 new fails = same 500 NPE from SurveyRest on /u1/urlPools (DELETE + activate)
- Suspect: SurveyRest NA-2051 (33af1854c70a, adam.szotak) — only QA deploy on that path; verify deploy diff

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9660100)
