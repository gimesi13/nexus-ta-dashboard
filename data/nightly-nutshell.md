**13 new failures — mainly PES, Fieldwork**

_Likely cause: VCS changes present but none map onto the failing packages — likely test/data, correlate manually._

- 7× PES soft-launch vs tally — java.lang.NullPointerException:Cannot invoke \
- 6× server NestedServletException / NPE — java.lang.NullPointerException:Cannot invoke \

⚠️ Contract drift: 6 new response-schema violation(s) vs baseline.
- DELETE /u1/nexus/urlPools/{} :: Response status 500 not defined for path '/u1/nexus/urlPools/{urlPoolId}'.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9660100)
