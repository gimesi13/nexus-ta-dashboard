**4 continuing QA backend failures — no new fails and no code changes to blame.**

_Likely cause: QA backend 500s (Lookup optionAssembler NPE, Communication scheduler ResourceNotFound) plus one assertion — not infra timeouts, and no commit in the window to implicate._

- Lookup optionAssembler returns 500 (NPE on `progress`) ×2; Communication PUT returns 500 (scheduler ResourceNotFound) + 1 assertion — all continuing from prior.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9650456)
