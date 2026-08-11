**412 new failures across AudienceGroup, Fieldwork and Lookup — the new typed error-code assertions can't read valid API error responses.**

_Likely cause: test-code change NXS-13667 by gergely.gimesi (45817a8833bb) — the new NexusApiErrors helper returns null on valid API error responses, breaking assertions across AudienceGroup, Fieldwork and Lookup._

- 60× "Condition not satisfied" — NexusApiErrors.dkmsError/status(exception) returns null though the API returned a valid 400/404 (e.g. "Unsupported country! [countryIso:ZZ]")
- 15× NOT_FOUND assertions — same helper returns null on 500/404 for non-existent IDs; 1 BOS 502 is infra noise

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9456994)
