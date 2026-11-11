# Full catalog versus lexical top-4 tool discovery

Frozen-design synthetic pilot, November 11, 2026. Not an MCP protocol benchmark,
Anthropic Tool Search implementation or production-product comparison.

## Conditions and data

64 read-only function definitions: 8 synthetic application catalogs with 8 search
objects each. Eight business intents, each with an explicit-service request and
a paraphrased request: 16 request cases, grouped into 8 paired intent families.
The requests specify an exact quoted query and integer result limit. The oracle
contains a single correct function and exact arguments. Data and expected outputs
are AI-authored before measurement, not externally validated production tasks.

Compare full64 with lexical4. The lexical retriever lowercases ASCII alphanumeric
terms in user request and function name/description, removes the frozen stoplist,
then ranks by number of DISTINCT overlapping terms, breaking ties by function
name. It returns the top 4 even at zero score. It never sees gold labels or
examples, uses no embeddings, extra LLM call, retries or fallback to full catalog.
Descriptions and aliases are deliberately compact. Literal/paraphrase coverage
is an authored stress set, not a prevalence estimate of real user language.

Existing qwen2.5:7b and qwen3:8b, pinned by local digests before inference; Ollama
0.20.2 native /api/chat, think=false, temperature=0, seed=20261111, num_ctx=16384,
num_predict=160. Exactly 64 planned measured requests: 16 cases × 2 conditions ×
2 models. One seed only; cases within an intent and two models are not independent
samples. Sequential requests/models on the existing 16-GiB Mac. No paid APIs,
downloads or real service execution. Tool proposals are scored, never executed.

Randomize case order and paired condition order separately for each model with
seed 20261111. keep_alive=0 unloads after every response; record /api/ps before
each request, actual load/cache counters and total/load/prompt/eval durations.
Cold-load timing is descriptive, not production latency. Do not infer dollar costs.
No artificial overall/daily generation cap. Operational request timeout: 90s;
record errors and incomplete calls without automatic retry or model replacement.
An unavailable/failed cell is not a correctness success. A prompt count near the
context cap blocks an unqualified no-truncation claim.

## Outcomes and controls

Primary: exactly one native tool call with correct name AND exact valid query/limit
arguments AND a name present in that request's offered tools, counts/16 per model and condition, with 8/8 wording strata and paired
intent outcomes. Names and argument accuracy are reported separately.
Discovery recall: whether the correct tool is available, /16 and /8 by wording.
If recall is lost, do not attribute the failure solely to the language model.
Efficiency: actual prompt_eval_count, optional cached count, serialized definition
bytes and caller wall time. Report missing counters as unknown. Latency/no-cache
claims require supporting observations and remain local/descriptive.

Scoring accepts native argument objects or valid JSON-encoded argument objects,
requires exactly query and limit, query string equality and a finite, integral,
non-bool numeric limit equal to the requested count (3.0 and 3 are equivalent,
consistent with JSON Schema integer semantics). It rejects malformed/multiple/
wrong-name/wrong-query/wrong-limit calls.
Positive controls submit gold outputs for every case; negative controls alter
each field and representation. A separate analysis implementation recalculates
discovery sets and task accuracy from saved raw responses. Test oracles against
valid alternative representations, avoiding the earlier exception-class artifact.

Protocol, cases, catalog, schedule, model identities and actual implementation are
hash-frozen before the first measured Qwen request. INVARIANT implements/validates
the harness through its fixed acceptance workflow, preserving version, request,
native worker/reviewer usage and application evidence. The existing local Ollama
server runs the measured proposals separately; do not imply those requests ran
inside INVARIANT. Context filtering is the intervention; cached/shared setup,
outer orchestration and implementation-agent usage are separate accounting scopes.

No dataset/prompt tuning or reruns after outcomes, including null/mixed results.
An implementation or protocol defect yields a diagnostic rather than an invented
success. Publish a dedicated repository, complete evidence, factual chart and an
English post naming INVARIANT's actual role and linking its repository.
