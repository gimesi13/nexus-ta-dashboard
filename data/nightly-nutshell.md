**4 continuing failures (0 new) — product-side 500s, not infra: a quotaGroups 'progress' NPE and a communication 500, plus one assertion.**

_Likely cause: product-side 500s (a quotaGroups 'progress' NPE and a communication 500) plus one Spock assertion — not infra, none new, and no commit maps._

- 2× Lookup: 500 NPE 'Cannot assign field progress … is null' on quotaGroups/optionAssembler (one mislabeled as a 502).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9643992)
