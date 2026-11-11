What changes when an agent sees 4 tool definitions instead of 64?

I tested a fixed keyword shortlist against the full catalog on Qwen2.5 7B and Qwen3 8B: 64 local calls, eight synthetic intents, each phrased with an explicit service name and a paraphrase. No real services were called.

Exact usable calls, full catalog → top 4:
• Qwen2.5: 5/16 → 7/16
• Qwen3: 13/16 → 9/16

A usable call required the correct available function and exact query/limit arguments. Qwen2.5's higher exact score did not mean better function selection: correct function names fell from 14/16 to 9/16. Nine full-catalog calls and two shortlist calls picked the right function but kept quotation marks in the query, failing the exact-match check.

The shortlist retained the expected tool for 9/16 requests: 8/8 with explicit service names, only 1/8 with paraphrases. Seven of the 16 request cases therefore reached the model without the tool they needed.

Mean prompt tokens fell from 5,343.9 to 526.4 for Qwen2.5, and 5,351.9 to 534.4 for Qwen3. That reduction came with lost discovery coverage in this set.

This is a small, AI-authored stress set with compact descriptions, one seed and no fallback. It tests literal keyword overlap on older local models, not a production search system or Anthropic's Tool Search.

INVARIANT coordinated isolated implementation and six fixed harness checks; Ollama ran the measured calls separately.
https://github.com/Xenox-developer/invariant

Code, raw responses and protocol:
https://github.com/Xenox-developer/tool-catalog-prefilter

Engineering context:
https://www.anthropic.com/research/advanced-tool-use
