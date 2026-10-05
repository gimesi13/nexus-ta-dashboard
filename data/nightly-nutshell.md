**2 new Project failures are a test-code bug — ProjectHelper manager-update methods called with a null id.**

_Likely cause: test-code defect — ManagersTestSteps passes a null manager id into ProjectHelper.updateAccountManager()/updateClientDeliveryConsultant(); no product or infra change._

- 2× Project/ManagersTestSteps — MissingMethodException: method called with (Integer, null), no matching overload.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9590724)
