**1 new failure in PartnerEvent: a create-validation test got a 404 instead of the expected field-validation error.**

_Likely cause: assertion failure on POST /u1/nexus/partnerEvents (owned by ExternalEventRest, migrated to J21 this window — NXS-13533, andras.banszki); backend change or test/data._

- PartnerEvent "Create partner event with invalid field values" — got HTTP 404, not an error naming the invalid field.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9572323)
