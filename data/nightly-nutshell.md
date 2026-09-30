**6 new failures — a QuotaGroup scheduling-wait regression (NXS-13972) plus 2 QA 502s.**

_Likely cause: NXS-13972 (gergely.gimesi) rewrote QuotaGroupSchedulingHelper's wait window — 4 new scheduling tests time out in waitForScheduleToRun; 2 further new fails are QA 502s (infra)._

- 4× new QuotaGroup: WaitUtil timeout ~187–190s in waitForScheduleToRun — schedule never ran
- 2× new QA 502 Bad Gateway (infra): BOS SalesOrder init; QuotaGroup 'Apply to all'

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) · [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_Gateways_NexusApi_RegressionTestQa_Nightly/9578565)
