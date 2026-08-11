**412 new failures — mainly AudienceGroup, Fieldwork**

_Likely cause: Possibly NXS-13667 by gergely.gimesi — touches AudienceGroup, Fieldwork, Lookup (79 overlapping new fails)._

- 60× assertion Condition not satisfied — Unsupported country! [countryIso:ZZ]
- 15× NOT_FOUND / missing data — org.springframework.dao.EmptyResultDataAccessException:No match in the given collections [[Projects, DraftProj

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9456994)
