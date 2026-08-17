**1 new Segment clone failure from a QA-side UnknownHostException (HTTP 500), no code changes in this build.**

_Likely cause: QA-side HTTP 500 rooted in an AWS SDK UnknownHostException (DNS/network); no build or QA-deploy changes, so infra/environment rather than a code regression._

- 1× Segment clone — QA 500 from SdkClientException/UnknownHostException (DNS/network, infra)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9471548)
