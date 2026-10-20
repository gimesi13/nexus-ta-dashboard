**2 new QuotaGroup failures from unsupported country-language combinations, not infra.**

_Likely cause: QuotaGroup country-language assertions (MA+[ar,en], BY+[de]) — test/data drift, no mapped code change._

- QuotaGroup clone BY+[de]: assertion expected "Unsupported country!" but got "Unsupported country-language combinations!".

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9624661)
