**76 new failures — QA microservices returning HTTP 500s (AbstractMethodError), not a test bug or code change**

_Likely cause: broken/mismatched QA deployment — no code changes shipped this build, so no commit or developer to attribute._

- QA 500s (AbstractMethodError on ExternalEvent, IndexOutOfBounds on DetailsEditor) are the root; validation/NOT_FOUND/assert fails cascade from them.
- No build changes (changes: []); prior build was a compile error — nothing attributable to a commit.

[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html) - [TeamCity](https://teamcity.dynata.com/buildConfiguration/Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt/9409083)
