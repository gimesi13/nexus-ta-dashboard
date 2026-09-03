**4 new failures — mainly Settings**

_Likely cause: No build changes — likely test/data or environment flakiness._

- 4× other — org.springframework.data.mongodb.UncategorizedMongoDbException:Command failed with error 13: 'Authorization fa

⚠️ Contract drift: 2 new response-schema violation(s) vs baseline.
- GET /u1/users/currentUser/userSettings :: Response status 500 not defined for path '/u1/users/currentUser/userSettings'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9505988)
