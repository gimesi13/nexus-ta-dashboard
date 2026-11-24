**2 new failures: a Segment assertion overlapping NXS-14576 and a QuotaGroup wait-timeout (infra).**

_Likely cause: mixed — the Segment assertion overlaps gergely.gimesi's test change NXS-14576; the QuotaGroup fail is a 45s WaitUtil timeout (infra/async)._

- 1 Segment assertion overlaps NXS-14576 (gergely.gimesi); 1 QuotaGroup WaitUtil timeout reads as infra.

⚠️ Contract drift: 3 new response-schema violation(s) vs baseline (e.g. PATCH …/endlinkSecurity 500).

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9703643)
