**1 new failure: an AudienceGroup undelete that wrote OK but didn't converge on read-back in QA; no code changes in the window.**

_Likely cause: read-after-write convergence timeout on AudienceGroup undelete (PUT succeeded, GET still isDeleted=true after 15s) with no commits in the window — most likely test/environment timing flakiness._

- New (1×): AudienceGroup "Undelete audience group with valid undelete" — PUT succeeded but GET still isDeleted=true after 15s (read-after-write convergence lag).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9609977)
