**3 continuing Communication failures (HTTP 400 quota-group-language validation) — no new failures.**

_Likely cause: test/data — HTTP 400 quota-group-language validation from dk-project-communication-rest, not infra and not mapped to any QA-deployed service._

- 3× Communication — HTTP 400 'Topic language is not a quota group language: hu' (continuing, not new)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9676621)
