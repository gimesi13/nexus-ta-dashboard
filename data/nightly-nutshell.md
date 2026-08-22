**1 new failure in Fieldwork**

_Likely cause: an assertion (deliveryMode MANUAL vs SLOWEST), not the 504 its label implies; no build changes to blame._

- Fieldwork delivery-mode assertion: got MANUAL, expected SLOWEST (not a 504)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9484034)
