**76 new failures — mainly Segment, QuotaGroup**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 31× server NestedServletException / NPE — org.springframework.web.util.NestedServletException:Handler dispatch failed; nested exception is java.lang.Abs
- 16× assertion Condition not satisfied

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9409083)
