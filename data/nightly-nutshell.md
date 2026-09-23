**4 new Project failures from NXS-11782 project-dates validation change (david.nagy)**

_Likely cause: david.nagy's NXS-11782 reworked project-date validation (UProjectDatesImpl.java); PUT proposedStartDate/proposedEndDate now return 500 with jakarta.validation.ValidationException._

- 3× 500 ValidationException on PUT project date endpoints — NXS-11782 (david.nagy); contract drift flags both
- 1× Project E2E totalQuota assertion (+100 update not applied)

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9539705)
