**Nightly build failed on a Gradle exception at the Clean Test step — 0 tests ran, no new test failures.**

_Likely cause: build/infra — a Gradle exception at the 'Clean Test' step (exit code 1) stopped the run before any tests executed._

- 0 tests ran (92s) vs 1456 passing prior, and the test module has no new commits, so no product change is implicated.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9683837)
