# Results

All 64 planned cells completed once and were independently rescored; no model request was replayed. The readiness-only interruption after the first call and continuation of 63 unissued cells are preserved in evidence/initial-stop.json and evidence/continuation.json. No prompt, fixture, model, metric or planned cell was changed. The recovery adapter was hash-recorded before continuation; its commit followed the start of continuation after a staging command referenced an as-yet-uncreated audit file. Frozen original source hashes and saved first response bytes are unchanged.

| Model | Condition | Correct function | Exact usable call | Tool available | Explicit exact | Paraphrase exact | Mean prompt tokens | Median cold response, s |
|---|---|---|---|---|---|---|---|---|
| qwen2.5:7b | full64 | 14/16 | 5/16 | 16/16 | 4/8 | 1/8 | 5343.9375 | 26.831 |
| qwen2.5:7b | lexical4 | 9/16 | 7/16 | 9/16 | 7/8 | 0/8 | 526.3750 | 5.338 |
| qwen3:8b | full64 | 13/16 | 13/16 | 16/16 | 8/8 | 5/8 | 5351.9375 | 35.395 |
| qwen3:8b | lexical4 | 9/16 | 9/16 | 9/16 | 8/8 | 1/8 | 534.3750 | 9.013 |

The lexical shortlist retained the expected tool for 9/16 requests: 8/8 explicitly named requests and 1/8 paraphrases. The same deterministic shortlist is used for both models. The seven missing tools are retrieval failures before the language model chooses a function, not evidence that either model forgot a tool it received.

The conditions changed different error types. Qwen2.5 selected the correct function 14/16 times with the full catalog and 9/16 with the shortlist. Among correctly named calls, nine full-catalog responses and two shortlist responses included literal quotation delimiters in query; those failed the preregistered exact query metric. Thus its 5/16 versus 7/16 exact success is not a gain in function selection. Qwen3's exact counts equaled its function-name counts: 13/16 versus 9/16. No model-wide winner or generalized claim is inferred.

Mean prompt counts fell from 5,343.9375 to 526.375 for Qwen2.5 and 5,351.9375 to 534.375 for Qwen3. Serialized tool definitions averaged 31,424 versus 1,971.375 bytes. All 64 responses had done=true and done_reason=stop; none reached the configured generation limit. All prompt counts were below the 16,384 context cap (maximum 5,356); this is an observed counter check, not a tokenizer-level proof. The optional cached-token counter was absent on all 64 responses and remains unknown.

The response latency figures include cold model loading and the API round trip, exclude shortlist computation and transport readiness waits, and are descriptive on one Mac. Do not extrapolate production throughput, costs or generic cache benefits.

Eight intent families, two authored wordings each, one seed, compact descriptions, no fallback and older local Qwen models limit generalization. This tests a literal token-overlap shortlist, not Anthropic's Tool Search, BM25, embeddings or an MCP product. No real tools were executed.

INVARIANT's isolated implementation/validation used 2 native Codex sessions / 5 observed provider responses / 50,228 total tokens. Those are separate from 64 local Ollama measurements. Full original receipts, worker observations and unknown outer-chat usage are documented in README.
