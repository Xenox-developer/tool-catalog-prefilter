# Primary sources checked November 11, 2026

- Anthropic, [Introducing advanced tool use](https://www.anthropic.com/research/advanced-tool-use), published November 24, 2025. Established context: discovering definitions on demand instead of always loading the entire catalog. This project does not implement or evaluate Anthropic Tool Search. No Anthropic benchmark numbers are reused.
- Ollama, [native chat endpoint](https://docs.ollama.com/api/chat), current documentation checked November 11, 2026. Native function definitions, non-streaming response fields, think=false, keep_alive=0 and timing/token counters. Keep-alive unload completion was observed to be asynchronous relative to the first response; see the recorded operational amendment.
- Ollama, [tool calling](https://docs.ollama.com/capabilities/tool-calling). This pilot only scores proposals and never executes a real service.
- JSON Schema, [numeric types](https://json-schema.org/understanding-json-schema/reference/numeric). An integral JSON number such as 3.0 satisfies integer semantics; the evaluator accepts it equivalently to 3.
- [INVARIANT](https://github.com/Xenox-developer/invariant), installed version 0.3.1. Actual role and verification receipts are in evidence/invariant.json.

The selected topic came from direct primary-source engineering research after a completed Telegram discovery collection. Telegram content and private channel inventories are not part of this public dataset. All 64 function definitions, 16 request cases and expected outputs are newly AI-authored synthetic fixtures, released with this repository. No production service data, account access, external source code or article text is redistributed.
