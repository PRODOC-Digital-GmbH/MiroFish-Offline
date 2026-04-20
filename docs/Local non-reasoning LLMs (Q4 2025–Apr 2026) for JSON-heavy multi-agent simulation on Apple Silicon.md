# Local non-reasoning LLMs (Q4 2025–Apr 2026) for JSON-heavy multi-agent simulation on Apple Silicon

## Overview

This report surveys open-weight, instruction-tuned LLMs released between October 2025 and April 2026 that are suitable as local backends for a JSON-heavy, multi-agent simulation platform on Apple Silicon (Mac Studio M4 Max, 128 GB RAM) using Ollama with an MLX backend.
The goal is to identify models with no always-on chain-of-thought, strong JSON adherence via OpenAI-compatible `response_format=json_object`, solid instruction following for NER/persona/social content, and throughput at least comparable to `qwen2.5:14b` for 380-word chunks under 32k context.[^1][^2]
The analysis excludes models whose primary design centers on explicit reasoning modes with `<think>` / `<nothink>`-style traces that are difficult to fully suppress in local deployments.[^3][^4]

## Hard requirements restated

The target deployment profile assumes:

- **No automatic chain-of-thought**: Models that embed explicit reasoning sections such as `<think> ... </think>` by default (Phi-4-Reasoning, Qwen3-Thinking, Ministral Reasoning variants, DeepSeek-R1, GLM-4.7 “thinking”) are excluded.
  These models are known to emit long reasoning segments conditioned on prompt style, and community reports confirm that such outputs can be hard to reliably strip in JSON-centric pipelines.[^4][^5][^3]
- **Reliable JSON output**: Models must be documented or broadly reported to work with structured output / JSON mode or function calling, where `response_format={"type":"json_object"}` guarantees syntactic validity when paired with appropriate prompting.[^6][^7]
- **Strong instruction following**: Focus on instruction-tuned "Instruct" or "chat" checkpoints designed for assistants and agents, with explicit support for system prompts and function/JSON outputs (e.g., Ministral-3 Instruct, Llama 3.1 Instruct, Phi-4 Instruct).[^8][^9]
- **Parallelizable**: Models must be available as GGUF or in the Ollama registry, i.e., runnable via `ollama run` or `ollama serve` with multiple concurrent requests.
  Community benchmarks and vendor docs show such models running stably on Mac Apple Silicon and CPUs under llama.cpp/Ollama.[^10][^11]
- **Size & memory**: Models between ~7B and 32B parameters, typically quantized at **Q4_K_M** or **Q8_0**, with a full 32k context plus KV cache fitting comfortably within ≤40 GB unified memory.
  Practical GGUF tables show Q4_K_M at ~4.4–9 GB disk for 7–14B models, implying well under 40 GB total, even with 32k context and KV overhead.[^12][^13]
- **Speed**: Community benchmarks indicate that 7–14B models in Q4/Q8 quantizations achieve ~30–100 tokens/s on M4/M3 Max, so the report prioritizes models in that envelope.[^14][^10]

The models already validated by the user—Qwen2.5-14B/32B and Ministral-3 14B Instruct—serve as baselines rather than candidates.

## Shortlist and ranking rationale

Because most post–Q4 2025 open-weight releases trend toward hybrid reasoning, truly non-reasoning models in the 7–32B range are relatively scarce.[^15][^16]
The ranking below prioritizes:

1.
JSON tooling and structured output support (native JSON mode, function calling, strong adherence in practice).
2.
Instruction tuning quality for NER, persona simulation, and social media style.
3.
Throughput per token on Apple Silicon at Q4_K_M/Q8_0.
4.
Evidence that the default templates do **not** inject explicit "thinking" sections.

The most relevant models for new experiments are:

1.
Ministral 3 14B Instruct 2512 (GGUF via LM Studio / Unsloth)
2.
Ministral 3 8B Instruct 2512
3.
Phi-4 14B Instruct (non-reasoning)
4.
Phi-4-mini Instruct (3.8B) as a low-cost helper agent
5.
Meta Llama 3.1 8B Instruct (updated GGUF quantizations)
6.
Meta Llama 3.3 8B Instruct (where available as GGUF) – experimental

Command R+ and Llama 4 Scout/Maverick are excluded on size and/or hybrid reasoning grounds, even though they can be made to run locally, because their parameter count and MoE footprint exceed the 32B/40 GB practical bound.[^17][^18]

## Candidate details and fit analysis

### 1.
Ministral 3 14B Instruct 2512 (Mistral)

**Why it fits**

Ministral 3 is Mistral AI’s late-2025 family of open-weight multimodal models in 3B, 8B, and 14B sizes, with separate Base, Instruct, and Reasoning variants.[^19][^20]
The **Instruct 2512** variant for 14B is explicitly tuned for chat and instruction tasks and is distinct from the Reasoning checkpoint that carries explicit chain-of-thought behavior.[^21][^22]
The GGUF export `Ministral-3-14B-Instruct-2512-GGUF` is available via LM Studio and Hugging Face, with multiple quantizations including Q4_K_M and Q8_0.[^23][^24]

**Release window and availability**

- LLM24 and Mistral model catalogs list the Ministral 3 family (3B/8B/14B, Base/Instruct/Reasoning) with a release date of **2025-12-02/04**, squarely within the requested window.[^25][^20]
- GGUF quantizations were pushed on Hugging Face on 2025-12-01 and updated by LM Studio in early 2026.[^24][^23]
- A dedicated GGUF variant from Unsloth (`unsloth/Ministral-3-14B-Instruct-2512-GGUF`) provides optimized quantizations for llama.cpp/Ollama import.[^22]

**JSON and function support**

Mistral’s Ministral Instruct models are advertised as "agentic" with **native function calling and JSON outputting**, mirroring the structured-output tooling available in the hosted Mistral API.[^9][^8]
Documentation and platform descriptions emphasize that Ministral 3 Instruct is designed for agents, including function calling and JSON schemas, making it well suited for `response_format=json_object` workflows when paired with appropriate prompts.[^26][^8]

**Chain-of-thought profile**

- The **Reasoning** variants of Ministral 3 include explicit thinking sections and are meant for math/coding tasks; the **Instruct** checkpoint instead focuses on fast, concise assistant behavior.[^21][^19]
- Community reviews of Ministral 3 8B/14B Instruct describe them as "yappy" but do not report hard-coded `<think>` blocks, unlike Magistral or Qwen3-Thinking.[^27]
- Mistral’s own product matrix clearly separates Instruct from Reasoning SKUs, which suggests the Instruct model should not be emitting mandatory chain-of-thought tags by default.[^19]

**Parameter count, quantizations, and memory**

- Ministral 3 14B is described as a **13.5B language model** plus a small vision encoder (~0.4B), i.e.
roughly 14B effective parameters.[^23]
- GGUF tables for similar 14B models show Q4_K_M files around **9–9.5 GB**, and Unsloth notes that Ministral 3 14B fits in **24 GB VRAM in FP8**, "less if further quantized".[^13][^22]
- With Q4_K_M and a 32k context, total memory (model + KV cache + runtime buffers) is estimated to remain safely under **30–35 GB** on unified memory Macs, within your 40 GB budget.

**Throughput on Apple Silicon**

There is no direct M4 Max benchmark yet, but comparable 14B Q4_K_M models (Phi-4 and Gemma 3 12B/27B) on an M4 Max MacBook Pro reach **~38 tokens/s for phi4:14b-q4** and **~22–44 tokens/s for Gemma 3 12–27B**, implying Ministral 3 14B Q4_K_M should be in a similar 25–40 tokens/s band.[^14]
Mistral’s own latency metrics for Ministral 3 8B/14B in hosted environments show high throughput (200+ tokens/s on server GPUs), again indicating a well-optimized architecture.[^28][^29]

**JSON reliability and caveats**

- Hosted Mistral models in JSON mode guarantee valid JSON when `response_format` and schema guidance are used; this behavior typically carries over to GGUF when using structured decoding (llama.cpp/Ollama response_format).[^7][^6]
- Users have reported that earlier Mistral 7B models can fail JSON-only prompts unless JSON mode is explicitly enabled, but this appears to be an issue of prompting rather than model incapability.[^30]
- The main caveat is verbosity: community notes mention that Ministral 3 Instruct is quite verbose ("+160% tokens" vs 2410 predecessors), which may impact throughput per call in simulations.[^27]

Overall, Ministral 3 14B Instruct is a strong, modern successor to Ministral-3 14B Instruct 2512 you already like, with explicit JSON support and no built-in reasoning mode, making it the top candidate.

### 2.
Ministral 3 8B Instruct 2512 (Mistral)

**Why it fits**

Ministral 3 8B Instruct 2512 is the mid-size member of the Ministral 3 family, with **8.4B language parameters plus 0.4B vision encoder**.[^8][^9]
It shares the same Instruct vs Reasoning split as the 14B model and is marketed as a "balanced model" for local/edge deployments, explicitly supporting **function calling and JSON output**.[^31][^8]

**Release window and availability**

- Mistral and third-party catalogs list the 8B Instruct 2512 SKU as released on **2025-12-04**, with GGUF variants available shortly after.[^32][^20]
- GGUF quantizations are provided by Mistral and LM Studio (`Ministral-3-8B-Instruct-2512-GGUF`), including Q4_K_M and Q8_0.[^33][^31]
- Ollama does not yet have an official Ministral-3 8B tag, but GGUF import via `ollama create` should be straightforward; llama.cpp v0.14+ lists Ministral-3-8B-Instruct-2512 as a supported architecture.[^34][^35]

**Chain-of-thought profile**

Like the 14B Instruct, the 8B Instruct checkpoint is distinct from **Ministral 3 8B Reasoning**, which is explicitly described as "reasoning capable" with chain-of-thought training.[^21][^19]
The Instruct variant is documented as a general assistant with function calling and JSON output, without any mention of built-in reasoning modes or `<think>` tokens.[^8]
Community benchmarks comparing Ministral 3 8B to Qwen3 reasoning models treat it as a non-reasoning counterpart.[^19]

**Parameter count, quantizations, and memory**

- 8.4B language + 0.4B vision ≈ 8.8B parameters, rounded to 8B in product names.[^8]
- GGUF tables and vendor docs indicate that quantized 8B models at Q4_K_M occupy roughly **4.5–5 GB** of disk and require **<12 GB** unified memory, even at large contexts.[^36][^31]
- Haimaker’s GGUF listing for Ministral 3 8B Instruct specifies deployment on constrained systems and notes that quantization brings the RAM/VRAM footprint down well below 12 GB.[^31]

**Throughput on Apple Silicon**

Although direct M4 Max measurements for Ministral 3 8B are not yet published, benchmarks for similar 7–8B models (Mistral 7B, Llama 3.1 8B, Llama 3.3 8B) in Q4_K_M on M2/M3 Macs show **30–50 tokens/s**, and often faster on M4.[^2][^37]
Given Ministral 3’s edge-optimized design, it is reasonable to expect throughput at least on par with `qwen2.5:14b` and likely faster.

**JSON reliability and caveats**

JSON mode caveats mirror the 14B Instruct model: interactions should use `response_format=json_object` and explicit schema guidance for best results.
Because Ministral 3 Instruct is built for agentic tasks, its adherence to JSON and function-output schemas is documented as a key feature.[^26][^8]
As with the 14B variant, verbosity is a known trade-off, which may slightly increase average latency per 380-word document segment.

Ministral 3 8B Instruct is therefore recommended as a **faster, lighter alternative** to the 14B model for helper agents or where simulation throughput is critical.

### 3.
Phi-4 14B Instruct (Microsoft, non-reasoning)

**Why it fits**

Phi-4 is Microsoft’s flagship **14B small language model** (SLM) that delivers strong reasoning and STEM performance at small scale but is also released in non-reasoning variants suitable for local deployment.[^38][^39]
Unlike Phi-4-Reasoning, which is explicitly trained to produce `<think>` chain-of-thought sections, the base/instruct Phi-4 weights do not embed mandatory thinking tokens and behave as standard instruction models.

**Release window and availability**

- Phi-4 was introduced as an open-weight model in late 2024 and continued to be developed into 2025, with GGUF quantizations and Ollama tags (`phi4:14b`) widely available by early 2025.[^40][^41]
- GGUF quantizations such as `phi-4-Q4_K_M.gguf` (bartowski) and others from EasierAI and Inferless provide Q4_K_M, Q4_K_S, and other recommended formats, with explicit notes about Apple Silicon optimization.[^42][^13]
- Ollama’s library exposes a `phi4:14b` model, and community reports confirm it runs well on M4 Max with Q4 and Q8 quantizations.[^43][^14]

**Chain-of-thought profile**

- The **Phi-4-Reasoning** and **Phi-4-Reasoning-Vision-15B** models are explicitly trained with `<think>` / `<nothink>` sections and chain-of-thought supervision.[^44][^3]
- Microsoft’s technical report warns that reasoning samples include `<think>...</think>` and are intended for tasks that benefit from long reasoning traces.[^45][^44]
- By contrast, the base Phi-4 14B instruct model does **not** use this hybrid reasoning template, and community deployments (e.g., in local LLaMA setups or PydanticAI JSON workflows) report standard assistant-style outputs without hidden reasoning segments.
  Local users highlight Phi-4 14B as "underrated" and suitable for structured tasks when combined with Pydantic for JSON, without mention of `<think>` tokens leaking.[^46][^47]

Given that your constraints exclude models with embedded `<think>` tags, the recommendation is to use **`phi4:14b` (non-reasoning)** and explicitly avoid any GGUF or Ollama variants labeled `reasoning`, `reasoning-plus`, or `mini-reasoning`.

**Parameter count, quantizations, and memory**

- Phi-4 is a 14B parameter model with a 16k context window in its default configuration.[^48][^38]
- Bartowski’s GGUF collection lists **`phi-4-Q4_K_M.gguf`** at **9.05 GB** and describes it as the recommended, balanced-quality quantization, explicitly noting good tokens-per-watt on Apple Silicon.[^13]
- Disk size and RAM needs are therefore similar to Ministral 3 14B: expect total memory consumption well below **30–35 GB** for 32k context, satisfying your ≤40 GB constraint.

**Throughput on Apple Silicon**

A Reddit benchmark on a MacBook Pro M4 Max measuring story generation found:

- `phi4:14b` Q4 quantization at **38.18 tokens/s**
- `phi4:14b` Q8 quantization at **27.29 tokens/s**

on a 16-core CPU, 40-core GPU, 128 GB RAM M4 Max configuration, very close to your Mac Studio profile.[^14]
Another community survey reports Phi-4 14B reaching ~40 tokens/s on GPUs similar to an RTX 3090, indicating good overall efficiency for its size.[^49]

**JSON reliability and caveats**

Phi-4’s hosted API supports JSON mode in Azure and GitHub Models, where `response_format={"type": "json_object"}` yields valid JSON and automatically removes reasoning in JSON mode.[^50][^39]
Although these guarantees are specific to their cloud deployment, they suggest that the model’s token distributions strongly favor syntactically valid JSON when guided.
Local users report 100% success on structured text manipulation tasks with `phi4:14b` at temperature 0 when the prompt enforces strict formatting.[^47]

The key caveat is to **avoid the reasoning variants**, which introduce `<think>` sections; these would violate your non-reasoning requirement.

### 4.
Phi-4-mini (3.8B) Instruct (Microsoft)

**Why it fits**

Phi-4-mini is a **3.8B** parameter small model in the Phi-4 family, designed as a compact but capable reasoning and instruction model with **128k context**.[^48]
The **Instruct** variant available as `phi4-mini` in Ollama and as GGUF via Unsloth is tuned for instruction following and function calling.
Although smaller than your 7–32B ideal range, it can serve as a low-latency helper agent for simpler NER tasks or routing.

**Release window and availability**

- Phi-4-mini was released alongside Phi-4 in early 2025 and popularized by local LLM guides and YouTube benchmarks throughout 2025.[^51][^48]
- Ollama hosts `phi4-mini` with a requirement of Ollama 0.5.13+, and Unsloth provides a `Phi-4-mini-instruct-GGUF` repository for conversion/export to GGUF and Ollama.[^52][^53]

**Chain-of-thought profile**

The **reasoning** variants of Phi-4-mini use chain-of-thought data, but the `phi4-mini-instruct` variant is positioned as a general-purpose model without mandatory reasoning sections.[^54][^4]
Ollama’s `phi4-mini` library entry does not mention `<think>`-style behavior or hybrid reasoning parameters, and community usage primarily treats it as a fast, compact instruction model.

**Parameter count, quantizations, and memory**

Local AI guides cite Phi-4-mini as a 3.8B model with VRAM use around **3 GB** at Q4 on GPUs, implying a similar scale on unified memory Macs.[^48]
At Q4_K_M or Q8_0, this model will be trivial to host within your 40 GB memory envelope, even at 32k or 128k context windows.

**Throughput on Apple Silicon**

While explicit M4 benchmarks for Phi-4-mini are sparse, a video benchmark indicates that Phi-4-mini runs "very fast" under LM Studio and Ollama on consumer hardware, and its parameter count suggests speeds well above **60–100 tokens/s** on an M4 Max at Q4.[^51][^2]
This makes it ideal for inexpensive helper agents in multi-agent simulations.

**JSON reliability and caveats**

Phi-4-mini inherits JSON mode and function calling from the Phi-4 family, and Ollama’s model card explicitly highlights function calling.[^52]
Because of its smaller capacity, however, its NER and persona quality will not match 14B/14B+ models.
It is best used for simpler tagging or routing tasks rather than complex persona simulation.

### 5.
Meta Llama 3.1 8B Instruct (updated GGUF for local)

**Why it fits**

Llama 3.1 8B Instruct remains one of the strongest non-reasoning open-weight models for generic instruction-following, with wide GGUF support and proven compatibility with llama.cpp and Ollama.
Although originally released in mid-2024, updated GGUF quantizations and deployment guides were published through 2025–2026, making it a practical option alongside newer models.[^55][^56]

**Release window and availability**

- Meta released Llama 3.1 in July 2024; however, updated GGUF builds such as `Meta-Llama-3.1-8B-Instruct-GGUF` and derivative packs (ARM-optimized, imatrix) continue to be released in 2025–2026.[^57][^56]
- LM Studio and Skywork provide web UIs and free chat endpoints for Meta-Llama-3.1-8B-Instruct-GGUF, with Q4_K_M and Q8_0 variants available.[^58][^59]
- The model is fully supported in llama.cpp, and conversion guides show how to turn the HF weights into GGUF for local inference; Ollama can import these via `ollama create`.[^11]

**Chain-of-thought profile**

Llama 3.1 8B Instruct was not trained as a reasoning model and does not use `<think>`-style chain-of-thought tokens.
It is a standard instruction-tuned decoder-only transformer, and there is no evidence of hybrid reasoning modes similar to Phi-4-Reasoning or Qwen3-Thinking.[^60]
Community use in projects like OpenMRS ChartSearchAI relies on Llama 3.x Instruct GGUF for structured, cited output without needing to strip hidden reasoning sections.[^61]

**Parameter count, quantizations, and memory**

- 8B parameters, with official docs and GGUF repos showing Q4_K_M models around **4.5–5 GB** in size.[^59][^56]
- Skywork AI notes that Meta-Llama-3.1-8B-Instruct-GGUF runs on **8–16 GB** VRAM at Q4_K_M, making it trivial to host on a 128 GB M4 Max, even with large contexts.[^59]

**Throughput on Apple Silicon**

A developer comparison of local LLM runtimes cites Llama 3.3 8B and Mistral Small 3 7B running at **30–50 tokens/s** on M2/M3 MacBook Pros with Q5_K_M, suggesting comparable or better performance on M4 Max for Llama 3.1 8B.[^2]
Given its smaller parameter count relative to 14B models, it should meet or surpass your current `qwen2.5:14b` baseline in tokens/s.

**JSON reliability and caveats**

Llama 3.x models support structured outputs and function calling in various hosted endpoints; local GGUF deployments rely on standard JSON-guidance techniques.
Projects that integrate Llama 3.x with structured output frameworks (e.g., PydanticAI) report stable JSON adherence when temperature is low and schemas are explicit.[^62][^61]
However, JSON compliance is not as strongly advertised as for Ministral 3 or Command R+.

### 6.
Meta Llama 3.3 8B Instruct (experimental)

**Why it is interesting but tentative**

Llama 3.3 8B Instruct is a later iteration in the Llama 3.x line, with improvements in context length (up to 131k), reasoning, and multilingual performance.[^63][^60]
It appears in multiple benchmarks and deployment guides by early 2026, and dynamic GGUF quantizations for Llama 3.3 8B Instruct are referenced in community repositories.[^64][^62]

**Release and availability**

- Wikipedia lists Llama 3.3 as released in December 2024, but community-shared GGUF and deployment content extends into 2025–2026, including 8B Instruct variants.[^65][^60]
- Local tools and model lists reference **"Meta-Llama-3.3-8B-Instruct-GGUF"** and derived models like "Llama3.3-8B-Thinking"; the latter should be avoided because it is a community fine-tune with explicit thinking behavior.[^66][^67]

**Chain-of-thought profile**

Meta’s official Llama 3.3 8B Instruct is not a reasoning model per se, but some community fine-tunes (e.g., "Llama3.3-8B-Thinking" or hybrids with Claude) add explicit reasoning outputs.[^67][^62]
These should be treated like DeepSeek-R1 or Qwen3-Thinking and excluded from production.
If using Llama 3.3 8B Instruct, select only the **official** Instruct GGUF checkpoints without "Thinking" in the name.

**Parameter count, quantizations, memory, and speed**

- Parameter count remains 8B; Q4_K_M GGUF files for Llama 3.3 70B are ~40 GB, so the 8B Q4_K_M files should be in the **4–6 GB** range.[^65]
- A 2026 developer article cites running Llama 3.3 8B Instruct in Q4_K_M on local hardware, using the rule-of-thumb that Q4_K_M uses ~4.5 bits/parameter.[^62]
This implies memory usage similar to Llama 3.1 8B, well within your limit.

**JSON reliability and caveats**

Llama 3.3 8B Instruct is documented with function calling and structured output capabilities on hosted platforms.
However, there is limited public data yet on JSON error rates in local GGUF deployments, so this model should be considered experimental until you can run your own NER/JSON benchmarks.

## Excluded but notable models

### Mistral Small 4 (119B MoE)

Mistral Small 4, released March 2026, is a 119B MoE model with 6–6.5B active parameters per token, supporting configurable `reasoning_effort` and hybrid reasoning modes.[^68][^69]
Although it can be run locally on large GPUs and has configurable reasoning vs non-reasoning behavior, its overall parameter count and MoE footprint make it too large for your ≤40 GB memory constraint, especially at 32k context.
Moreover, the presence of a dedicated reasoning mode introduces the risk of inadvertent chain-of-thought exposure if prompts are not tightly controlled.[^70][^71]

### Phi-4 Reasoning (14B) and Phi-4-Reasoning-Vision-15B

These models are explicitly trained to produce `<think> ... </think>` sections and use special `<nothink>` tokens to switch modes.[^3][^44]
Microsoft’s technical report and documentation emphasize their hybrid reasoning nature, making them unsuitable for deployments that must avoid any internal reasoning output.
Even when trying to force non-reasoning outputs, the presence of `<think>` tokens in training data increases the risk of leakage.

### Qwen3-think / Qwen3-VL Thinking variants

Qwen3 and Qwen3-VL include "Thinking" variants with explicit reasoning tokens, similar to DeepSeek-R1 and Phi-4-Reasoning.[^44][^19]
Your constraints already exclude them due to reasoning leaks and difficulty enforcing `think:false`.

### GLM-4.7-Flash / GLM-4.7-Flash-GGUF

GLM-4.7 is a thinking-focused model that exhibits extended reasoning loops; users report that it "thinks" endlessly and requires special settings to behave, which conflicts with your requirement to avoid chain-of-thought entirely.[^72][^5]

### Command R+ (104B) and Command R (35B)

Cohere’s Command R+ (104B) and earlier Command R (35B) are open-weight RAG-native models with strong JSON and tool use but exceed your 32B parameter upper bound and, in the case of Command R+, your 40 GB memory limit at 32k context.[^73][^18]
Even with aggressive quantization, Command R+ Q4_K_M GGUF requires on the order of 60–70 GB RAM, which is not a comfortable margin for your Mac Studio.

### Llama 4 Scout / Maverick

Llama 4 Scout and Maverick are 17B active-parameter MoE models with total parameters in the hundreds of billions and maximum context windows up to 10M tokens.[^74][^17]
Community GGUF quantizations exist, but even 2–3 bit dynamic quantizations produce files in the 33–65 GB range, and recommended setups often assume multi-GPU or cloud hardware.[^75][^74]
Moreover, Llama 4 emphasizes multimodal reasoning and tool calling, increasing the risk of verbose or pseudo-reasoning outputs; they are therefore not recommended for your use case.

## Practical recommendations for MiroFish

### Top 3 priority models to test

For a multi-agent simulation with heavy NER and JSON, the following order of experimentation is recommended:

1.
**Ministral 3 14B Instruct 2512 (Q4_K_M)** – as a higher-quality successor to Ministral-3 14B Instruct with strong JSON/function support and no built-in thinking.
2.
**Ministral 3 8B Instruct 2512 (Q4_K_M)** – as a faster, lighter model for helper agents or high-throughput NER.
3.
**Phi-4 14B Instruct (Q4_K_M or Q8_0)** – as a strong generalist SLM with good JSON behavior and excellent Apple Silicon performance.

### Secondary models

- **Phi-4-mini 3.8B Instruct (Q4_K_M)** – for routing, simple tagging, or cheap persona variants.
- **Llama 3.1 8B Instruct (Q4_K_M)** – as a stable, non-reasoning workhorse if you need a non-Mistral, non-Microsoft baseline.
- **Llama 3.3 8B Instruct (Q4_K_M)** – experimental; only consider official Instruct variants and avoid community "Thinking" fine-tunes.

### JSON robustness and prompting tips

Given your sensitivity to JSON parse failures, the following practices are recommended regardless of model choice:

- Use `response_format={"type": "json_object"}` whenever possible to enforce JSON-only output in OpenAI-compatible interfaces (Ollama can proxy this via its OpenAI endpoint when configured appropriately).[^6][^7]
- Always include a **clear JSON schema or example object** in the system prompt, especially for NER tasks, to leverage models like Ministral 3 Instruct that support custom structured outputs.[^76][^77]
- Keep **temperature at 0 or very low** (≤0.2) for NER/JSON tasks to reduce creative deviations, as evidenced by 100% success reports for Phi-4 14B in structured text manipulation at temperature 0.[^47]
- Consider adding a lightweight **JSON validator agent** powered by a very small model (e.g., Phi-4-mini or a 1–3B Llama 3.x derivative) that can request regeneration if parsing fails, similar to workflows described for Mistral JSON Architect and other structured-output pipelines.[^78][^30]

With these configurations, the models above should all meet or exceed the performance of `qwen2.5:14b` for your 380-word NER chunks while respecting your constraints around chain-of-thought and local deployment on Apple Silicon.

---

## References

1. [Local AI 2026: Ollama Benchmarks, Hardware Costs vs Cloud APIs ...](https://pooya.blog/blog/local-ai-ollama-benchmarks-cost-2026/) - An M4 Max runs the 70B DeepSeek-R1 at 12 tokens per second because the full model fits in unified me...

2. [Best Local LLM Models 2026 | Developer Comparison - SitePoint](https://www.sitepoint.com/best-local-llm-models-2026/) - Run Llama 3.3 8B or Mistral Small 3 7B at Q5_K_M, and expect approximately 30 to 50 tokens per secon...

3. [microsoft/Phi-4-reasoning - Hugging Face](https://huggingface.co/microsoft/Phi-4-reasoning) - Phi-4-reasoning Model Card. Phi-4-reasoning Technical Report. Model ... Model responses have two sec...

4. [Phi-4 Reasoning: How to Run & Fine-tune | Unsloth Documentation](https://unsloth.ai/docs/models/tutorials/phi-4-reasoning-how-to-run-and-fine-tune) - Microsoft's new Phi-4 reasoning models are now supported in Unsloth. ... In the Thought section, det...

5. [unsloth/GLM-4.7-Flash-GGUF · Infinite thinking (after ... - Hugging Face](https://huggingface.co/unsloth/GLM-4.7-Flash-GGUF/discussions/14) - GGUF · English · Chinese · unsloth · imatrix · conversational. arxiv ... To get normal thinking or i...

6. [Structured Outputs - Mistral Docs](https://docs.mistral.ai/capabilities/structured_output) - For JSON mode, it is essential to explicitly instruct the model in your prompt to output JSON and sp...

7. [Mistral AI Guide — Models, API & Fine-Tuning for Engineers (2026)](https://myengineeringpath.dev/tools/mistral-guide/) - Important: When using JSON mode, you must instruct the model to produce JSON in your system or user ...

8. [mistralai/Ministral-3-8B-Instruct-2512 - Hugging Face](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) - Ministral 3 8B Instruct 2512. A balanced model in the Ministral 3 family, Ministral 3 8B is a powerf...

9. [mistralai/Ministral-3-8B-Instruct-2512-BF16 - Hugging Face](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-BF16) - Ministral 3 8B Instruct 2512 BF16. A balanced model in the Ministral 3 family, Ministral 3 8B is a p...

10. [Mistral-7B-Instruct-V0.3-GGUF Free Chat Online – skywork.ai](https://skywork.ai/blog/models/mistral-7b-instruct-v0-3-gguf-free-chat-online-skywork-ai/) - Noromaid Mixtral 8x7B Instruct Free Chat Online · Noromaid-20b-V0.1.1 Free Chat ... QuantFactory/Min...

11. [Running Large Language Models Locally Using Ollama](https://www.codemag.com/Article/264031/Running-Large-Language-Models-Locally-Using-Ollama) - In such cases, you can convert a model—like meta-llama/Llama-3.2-3B-Instruct —to GGUF. To do this, y...

12. [mertbozkir/metamath-mistral-7b:Q4_0 - Ollama](https://ollama.com/mertbozkir/metamath-mistral-7b:Q4_0) - This repo contains GGUF format model files for MetaMath's Metamath Mistral 7B. These files were quan...

13. [bartowski/phi-4-GGUF - Hugging Face](https://huggingface.co/bartowski/phi-4-GGUF) - Legacy format, similar performance to Q4_K_S but with improved tokens/watt on Apple silicon. phi-4-Q...

14. [New Google Gemma3 Inference speeds on Macbook Pro M4 Max](https://www.reddit.com/r/ollama/comments/1j9uxlr/new_google_gemma3_inference_speeds_on_macbook_pro/) - phi4:14b. Quantization, Load Duration, Inference Speed. q4, 25.423792ms ... Who have real experience...

15. [Mistral Small 4 supports configurable hybrid reasoning with ...](https://x.com/ArtificialAnlys/status/2034960206736892365) - In reasoning mode, Mistral Small 4 scores 27 on the Artificial Analysis Intelligence Index, a 12-poi...

16. [What Is Mistral Small 4? The Open-Weight Model You Can Fine ...](https://www.mindstudio.ai/blog/what-is-mistral-small-4/) - Mistral Small 4 is an open-weight model that matches Claude Haiku ... Chain-of-thought reasoning is ...

17. [Meta Llama - Hugging Face](https://huggingface.co/meta-llama) - We are launching two efficient models in the Llama 4 series, Llama 4 Scout, a 17 billion parameter m...

18. [Command R+ - D-Central](https://d-central.tech/ai/model/command-r-plus/) - Bigger picture: Command R+ is one more layer of decentralization in the open-weight landscape, speci...

19. [Ministral 3 3B Reasoning 2512 — 4.3B Parameter LLM | haimaker.ai ...](https://haimaker.ai/models/mistralai/ministral-3b-2512) - |Released Oct 2025 · Updated Jan 2026. Parameters. 4.3B.

20. [Mistral AI LLM Models - LLM24](https://llm24.net/organization/mistral) - Ministral 3 (8B Instruct 2512) · ministral-3-8b-instruct-2512, 2025-12-04, Show ... 2025-10-30, Show...

21. [mistralai/Ministral-3-14B-Reasoning-2512 - Hugging Face](https://huggingface.co/mistralai/Ministral-3-14B-Reasoning-2512) - Ministral 3 14B consists of two main architectural components: 13.5B Language Model; 0.4B Vision Enc...

22. [unsloth/Ministral-3-14B-Instruct-2512-GGUF - Hugging Face](https://huggingface.co/unsloth/Ministral-3-14B-Instruct-2512-GGUF) - Ministral 3 14B Instruct 2512. The largest model in the Ministral 3 family, Ministral 3 14B offers f...

23. [mistralai/Ministral-3-14B-Instruct-2512-GGUF - Hugging Face](https://huggingface.co/mistralai/Ministral-3-14B-Instruct-2512-GGUF) - Ministral 3 14B Instruct 2512 GGUF. The largest model in the Ministral 3 family, Ministral 3 14B off...

24. [lmstudio-community/Ministral-3-14B-Instruct-2512-GGUF](https://huggingface.co/lmstudio-community/Ministral-3-14B-Instruct-2512-GGUF) - Highlighting new & noteworthy models by the community. Join the conversation on Discord. Model creat...

25. [LLM pricing, benchmarks, and specifications - vantage.sh/models](https://www.vantage.sh/models) - 2025-10-01. 200000. 64000. 264000. 2025-07. $1.00. $5.00. Yes. basic. -. 66.6. -. No ... Ministral 3...

26. [Ministral 3 8B Instruct 2512 API - Together AI](https://www.together.ai/models/ministral-3-8b-instruct-2512) - Ministral 3 8B Instruct 2512. Balanced 8B multimodal model for versatile assistants, agents, and mul...

27. [First Impressions from discord - Dubesor LLM Benchmark](https://dubesor.de/first-impressions) - YMMV. Ministral 3 8B Instruct. Ministral 3 14B Instruct. 2025-12 ... 2025-10-28. Tested MiniMax-M2: ...

28. [Ministral 3 (8B Instruct 2512): Pricing, Benchmarks & Performance](https://llm-stats.com/models/ministral-3-8b-instruct-2512) - See how Ministral 3 (8B Instruct 2512) ranks against other models in each benchmark it participates ...

29. [MiniMax M2 vs Ministral 3 (8B Reasoning 2512) Comparison](https://llm-stats.com/models/compare/minimax-m2-vs-ministral-8b-latest) - MiniMax M2 was released on 2025-10-27, while Ministral 3 (8B Reasoning 2512) was released on 2025-12...

30. [Can Mistral small/medium models output valid json 100% of the time](https://www.reddit.com/r/MistralAI/comments/1lguhdf/can_mistral_smallmedium_models_output_valid_json/) - My experience is that it can't be guaranteed with Mistral. Some of my prompts always returns JSON an...

31. [Ministral 3 8B Instruct 2512 GGUF — LLM | haimaker.ai | haimaker.ai](https://haimaker.ai/models/mistralai/ministral-8b-2512) - Ministral 3 8B Instruct 2512 GGUF. A balanced model in the Ministral 3 family, Ministral 3 8B is a p...

32. [Claude Haiku 4.5 vs Ministral 3 (8B Instruct 2512) - LLM Stats](https://llm-stats.com/models/compare/claude-haiku-4-5-20251001-vs-ministral-3-8b-instruct-2512) - Claude Haiku 4.5 was released on 2025-10-15, while Ministral 3 (8B Instruct 2512) was released on 20...

33. [mistralai/ministral-3-8b - LM Studio](https://lmstudio.ai/models/mistralai/ministral-3-8b) - lmstudio-community/Ministral-3-8B-Instruct-2512-GGUF→. GGUF. Product. Download the appModelsLM LinkN...

34. [Supported Models - vLLM](https://docs.vllm.ai/en/v0.14.0/models/supported_models/) - Mixtral-8x7B, Mixtral-8x7B-Instruct, mistralai/Mixtral-8x7B-v0.1 ... mistralai/Ministral-3-3B-Instru...

35. [Ministral-3 Instruct Usage Guide - vLLM Recipes](https://docs.vllm.ai/projects/recipes/en/latest/Mistral/Ministral-3-Instruct.html) - Due to their size and the FP8 format of their weights Ministral-3-3B-Instruct-2512 , Ministral-3-8B-...

36. [mradermacher/Mistral-LLaMA-Fusion-GGUF - Hugging Face](https://huggingface.co/mradermacher/Mistral-LLaMA-Fusion-GGUF) - If you are unsure how to use GGUF files, refer to one of TheBloke's READMEs for more details, includ...

37. [Meta-Llama-3-8B-Instruct-GGUF Free Chat Online - skywork.ai ...](https://skywork.ai/blog/models/meta-llama-3-8b-instruct-gguf-free-chat-online-skywork-ai/) - Meta-Llama-3-8B-Instruct-GGUF represents a significant advancement in accessible AI technology. This...

38. [Deploy Phi-4-GGUF using Inferless - GitHub](https://github.com/inferless/phi-4-GGUF) - Phi-4 is Microsoft's latest 14 billion parameters small language model (SLM). This model is part of ...

39. [How LLMs Work: From Tokens to Transformers — Complete Guide ...](https://hyperion-consulting.io/resources/how-llms-work) - Phi-4, 14B, 16K, MIT, 84.8, Reasoning, STEM, small ... json" \ -d '{ "model": "meta-llama/Llama-4-Sc...

40. [phi4:14b-q4_K_M - Ollama](https://ollama.com/library/phi4:14b-q4_K_M) - Phi-4 is a 14B parameter, state-of-the-art open model built upon a blend of synthetic datasets, data...

41. [Microsoft Phi-4 GGUF available. Download link in the post - Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1hde9ok/microsoft_phi4_gguf_available_download_link_in/) - Model downloaded from azure AI foundry and converted to GGUF. This is a non official release. The of...

42. [Phi-4-14B-Q4_K_M.gguf - Hugging Face](https://huggingface.co/EasierAI/Phi-4-14B/blob/main/Phi-4-14B-Q4_K_M.gguf) - This file is stored with Xet . It is too big to display, but you can still download it. Large File P...

43. [phi4:14b - Ollama](https://ollama.com/library/phi4:14b) - Phi-4 is a 14B parameter, state-of-the-art open model built upon a blend of synthetic datasets, data...

44. [Phi-4-reasoning-vision-15B Technical Report - arXiv](https://arxiv.org/html/2603.03975v1) - Our model is trained with SFT, where reasoning samples include <think>...</think> sections with chai...

45. [Phi-4-reasoning-vision and the lessons of training a multimodal ...](https://www.microsoft.com/en-us/research/blog/phi-4-reasoning-vision-and-the-lessons-of-training-a-multimodal-reasoning-model/) - We used just 200 billion tokens of multimodal data leveraging Phi-4 ... Phi-4-reasoning-vision-15B –...

46. [Phi 4 is so underrated : r/LocalLLaMA - Reddit](https://www.reddit.com/r/LocalLLaMA/comments/1igf1vi/phi_4_is_so_underrated/) - In combination with PydanticAI where you can easily define an expected json format ... This is a mod...

47. [Performance Testing of LLMs on Text Manipulation in a Zettelkasten](https://gist.github.com/svetzal/9702677df35dd45f783a4a3a0f642d3d) - phi4:14b. This is a 14B parameter model from Microsoft. It achieved 100 ... I think it would be inte...

48. [Best Small AI Models for Ollama 2026: Phi-4, Gemma 3, Qwen 3 ...](https://localaimaster.com/blog/small-language-models-guide-2026) - Top 12 small language models you can run locally with Ollama. Phi-4 leads benchmarks. Gemma 3, Qwen ...

49. [Getting Started with Local AI: Run LLMs on Your Own Hardware ...](https://willitrunai.com/blog/getting-started-local-ai) - An RTX 3090 (24 GB), RTX 4080 (16 GB), or M2 Pro Mac fits here. ... ollama run qwen3:14b or ollama r...

50. [zpg6/langchain-azure-ai-inference-plus: Enhanced ... - GitHub](https://github.com/zpg6/langchain-azure-ai-inference-plus) - For JSON mode, reasoning is automatically removed so you get clean JSON: ... response_format ... llm...

51. [Open Sourced FREE Model using LM Studio & Ollama - YouTube](https://www.youtube.com/watch?v=T-whtkYhxd8) - ... Mini and Phi-4 Multimodal, see the benchmarks, evaluate the results after running on a local sys...

52. [phi4-mini - Ollama](https://ollama.com/library/phi4-mini) - Phi-4-mini-instruct is a lightweight open model built upon synthetic data and filtered publicly avai...

53. [unsloth/Phi-4-mini-instruct-GGUF - Hugging Face](https://huggingface.co/unsloth/Phi-4-mini-instruct-GGUF) - Unsloth's Phi-4 Dynamic Quants is selectively quantized, greatly improving accuracy over standard 4-...

54. [unsloth/Phi-4-mini-reasoning-GGUF - Hugging Face](https://huggingface.co/unsloth/Phi-4-mini-reasoning-GGUF) - Phi-4-mini-reasoning is a lightweight open model built upon synthetic data with a focus on high-qual...

55. [Deploy Meta-Llama-3.1-8B-Instruct-GGUF using Inferless - GitHub](https://github.com/inferless/llama-3.1-8b-instruct-gguf) - An 8B-parameter, instruction-tuned variant of Meta's Llama-3.1 model ... © 2026 GitHub, Inc. Footer ...

56. [uygarkurt/Llama-3.1-8B-Instruct-GGUF · Hugging Face](https://huggingface.co/uygarkurt/Llama-3.1-8B-Instruct-GGUF) - Llama-3.1-8B-Instruct-GGUF. like 0. Text ... instruction-tuned · local-inference · conversational .....

57. [Meta-Llama-3.1-70B-Instruct-GGUF Free Chat Online – skywork.ai](https://skywork.ai/blog/models/meta-llama-3-1-70b-instruct-gguf-free-chat-online-skywork-ai/) - ... Q4_K_M-GGUF Free Chat Online – skywork.ai, Click to Use! DeepSeek-R1-Distill ... Meta: Llama 3.3...

58. [Meta-Llama-3.1-8B-Instruct-128k-GGUF Free Chat Online - skywork ...](https://skywork.ai/blog/models/meta-llama-3-1-8b-instruct-128k-gguf-free-chat-online-skywork-ai/) - Meta-Llama-3.1-8B-Instruct-128k-GGUF Free Chat Online - skywork.ai, Click to Use ... Meta-Llama-3.1-...

59. [MaziyarPanahi/Meta-Llama-3.1-8B-Instruct-GGUF Free Chat Online](https://skywork.ai/blog/models/maziyarpanahi-meta-llama-3-1-8b-instruct-gguf-free-chat-online-skywork-ai/) - Meta: Llama 3.3 8B Instruct Free Chat Online · Meta: Llama 4 Maverick Free Chat Online · Meta: Llama...

60. [Llama (language model) - Wikipedia](https://en.wikipedia.org/wiki/Llama_(language_model)) - Llama 3.1, July 23, 2024, Active ; Llama 3.2, September 25, 2024, Active ; Llama 3.3, December 7, 20...

61. [openmrs-esm-chartsearchai - GitHub](https://github.com/openmrs/openmrs-esm-chartsearchai) - Generation -- the filtered records are sent to a local GGUF LLM (default: Llama 3.3 8B via llama.cpp...

62. [Running Local LLMs in 2026: Ollama, LM Studio, and Jan Compared](https://dev.to/synsun/running-local-llms-in-2026-ollama-lm-studio-and-jan-compared-5dii) - create( model="lmstudio-community/Meta-Llama-3.3-8B-Instruct-GGUF ... A rough guide: Q4_K_M at 4.5 b...

63. [Llama 3.3 70B Instruct vs. Qwen3 VL 8B Thinking - Galaxy.ai Blog](https://blog.galaxy.ai/compare/llama-3-3-70b-instruct-vs-qwen3-vl-8b-thinking) - In-depth analysis of Llama 3.3 70B Instruct vs Qwen3 VL 8B Thinking, revealing performance gaps, cos...

64. [XpressAI/shisa-v2.1-unphi4-14b-GGUF - Hugging Face](https://huggingface.co/XpressAI/shisa-v2.1-unphi4-14b-GGUF) - ... 2025-11-13 ) as our Shaberi LLM Judge. GPT-5.1 scores answers ... Llama-3.3-70B-Instruct, shisa-...

65. [Llama-3.3-70B-Instruct-GGUF Free Chat Online – skywork.ai](https://skywork.ai/blog/models/llama-3-3-70b-instruct-gguf-free-chat-online-skywork-ai/) - ... Meta: Llama 3.3 8B Instruct; Mistral: Devstral Small 1.1; Mistral Large; Meta ... Q4_K_M-GGUF; G...

66. [frob/mradermacher-Llama3.3-8B-Thinking-Heretic-Claude-4.5-Opus](https://ollama.com/frob/mradermacher-Llama3.3-8B-Thinking-Heretic-Claude-4.5-Opus) - Claude Code ollama launch claude --model frob/mradermacher-Llama3.3-8B-Thinking-Heretic-Claude-4.5-O...

67. [New Old Llamas - Hugging Face](https://huggingface.co/blog/mike-ravkine/new-old-llamas) - Llama-3.3-8B-Thinking (FP16) - A community fine-tune of 3.3 trained on Claude 4.5 Opus reasoning out...

68. [Introducing Mistral Small 4](https://mistral.ai/news/mistral-small-4) - Mistral Small 4 is a hybrid model optimized for general chat, coding, agentic tasks, and complex rea...

69. [Mistral Small 4 Complete Guide — Unified Reasoning, Multimodal ...](https://www.oflight.co.jp/en/columns/mistral-small-4-unified-reasoning-multimodal-2026) - Mistral Small 4, released March 2026, unifies reasoning, multimodal vision, and agentic coding in a ...

70. [Mistral Small 4 Review: Reasoning, Coding, and Multimodal in a ...](https://reeboot.fr/en/blog/mistral-small-4) - On mathematical reasoning tasks, Mistral Small 4 achieves a score of 0.72 while producing responses ...

71. [Mistral Small 4 Just Dropped — Run It on Affordable H200s ... - Vast.ai](https://vast.ai/article/mistral-small-4-just-dropped-run-it-on-affordable-h200s-with-vast-ai) - Mistral Small 4 is the first Mistral model to unify three previously separate families — instruct, r...

72. [GLM-4.7: How to Run Locally Guide | Unsloth Documentation](https://unsloth.ai/docs/models/tutorials/glm-4.7) - Llama 4 · Grok 2 · Devstral · Run Unsloth models in Docker · DeepSeek ... ollama serve & OLLAMA_MODE...

73. [LiteLLMs/c4ai-command-r-plus-GGUF - Hugging Face](https://huggingface.co/LiteLLMs/c4ai-command-r-plus-GGUF) - C4AI Command R+ is an open weights research release of a 104B billion parameter model with highly ad...

74. [Tutorial: How to Run Llama-4 locally using 1.78-bit Dynamic GGUF](https://www.reddit.com/r/LocalLLM/comments/1jujoc5/tutorial_how_to_run_llama4_locally_using_178bit/) - You can run Llama-4-Scout even without a GPU! Scout 1.78-bit runs decently well on CPUs with 20GB+ R...

75. [bartowski/meta-llama_Llama-4-Scout-17B-16E-Instruct-old-GGUF](https://huggingface.co/bartowski/meta-llama_Llama-4-Scout-17B-16E-Instruct-old-GGUF) - Quantizations of Llama-4-Scout-17B-16E-Instruct by meta-llama. Using llama.cpp release b5074 with my...

76. [Custom Structured Outputs - Mistral AI Documentation](https://docs.mistral.ai/capabilities/structured_output/custom) - Custom Structured Outputs allow you to ensure the model provides an answer in a very specific JSON f...

77. [Structured outputs with Mistral, a complete guide w - Instructor](https://python.useinstructor.com/integrations/mistral/) - This guide demonstrates how to use Mistral with Instructor to generate structured outputs. You'll le...

78. [Generate dynamic JSON output formats for AI agents with Mistral](https://n8n.io/workflows/5829-generate-dynamic-json-output-formats-for-ai-agents-with-mistral/) - (27)

