**2 new failures in QuotaGroup**

_Likely cause: VCS changes present but none map onto the failing packages — likely test/data, correlate manually._

- 2× GB + fr unsupported — Unsupported country-language combinations! [countryIso:MA] [languageIsos:[ar, en]]

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9624661)
