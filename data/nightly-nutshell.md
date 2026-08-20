**1 new failure in QuotaGroup**

_Likely cause: Possibly NXS-13726 by gergely.gimesi — touches QuotaGroup (1 overlapping new fails)._

- 1× client/Feign socket timeout — feign.RetryableException:timeout executing POST <url> Caused by: java.net.SocketTimeoutException:timeout

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9482712)
