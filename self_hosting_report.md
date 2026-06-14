# Self-Hosting Report

All numbers below are real, measured on **my** machine via Ollama's native `/api/chat` endpoint (which returns `load_duration`, `eval_count`, `eval_duration` etc.). RAM figures are from `ollama ps` (memory the loaded model occupies). Scripts used: `bench.py` (LLMs) and `vlm_bench.py` (VLMs).

**Test machine:** Intel Core i5-14450HX (16 threads), 16 GiB RAM, NVIDIA RTX 3050 6 GB Laptop GPU, Arch Linux, Ollama 0.30.8. Models ran on the GPU (not CPU) — except `llava:7b`, which spilled to CPU because its weights + context don't fit in 6 GB VRAM.

## Task 1 — Benchmark two local models

**Fixed prompt (identical for both):**

> "Explain what an inference engine is and why someone would self-host one instead of using a hosted API. Answer in about 4 sentences."

Load time = cold start (`ollama stop` first, so weights load from disk). Tokens/sec = generated tokens ÷ generation time.

| Model | Approx size / quant | Load time (s) | Tokens/sec | RAM used | Quality note |
| --- | --- | --- | --- | --- | --- |
| `qwen2.5:0.5b` | 0.5B (494M) / Q4_K_M | **2.23** | **166.8** | **481 MB** | Fast but loose: ignored the "4 sentences" limit (gave \~18), opened with a wrong definition ("an inference engine, or more commonly known as an AI-powered model"). Padded, listy. |
| `llama3.2:3b` | 3.2B / Q4_K_M | **19.08** | **52.5** | **2.6 GB** | Correct and tight: accurate definition (logic rules + facts → conclusions), obeyed the 4-sentence limit, named the real reasons (control, security, latency). |

**Trade-off you observed (2–3 sentences):**

> The 0.5B model loaded \~8.5× faster, ran \~3.2× more tokens/sec, and used \~5× less RAM — but it didn't follow the instruction and got the definition partly wrong. The 3B model paid for its quality with a slow cold start (19 s to page 2.6 GB of weights in) and a third of the throughput, yet its answer was accurate and concise. So the axis is real: tiny models are for speed/cheap-RAM/high-volume work where "roughly right" is fine, bigger ones for when the answer actually has to be correct and instruction-following.

## Task 2 — `local_client.py`

`local_client.py` calls `http://localhost:11434/v1` through the `openai` SDK (`base_url` swapped to localhost, dummy key). Verified output:

```
$ python local_client.py
An inference engine is a software component that uses logical rules and
database facts to draw conclusions or make decisions by deducing new
information from existing knowledge.
```

The file's comment block explains why this is the *same shape* as a hosted Gemini call: same HTTP POST, same `{model, messages:[{role,content}]}` body, same `choices[0].message.content` response, same SDK — only the `base_url`changed. An LLM is just a process on a socket; hosted vs. self-hosted is only *which machine* runs it.

## Task 3 — VLM: local vs hosted

**No Gemini key was available** (free tier not set up), so per the lab's fallback I compared **two local VLMs** instead: `moondream` (tiny) vs `llava:7b` (mid). Same image, same question.

Image used: `sample_chart.png` (provided, committed in repo) — a bar chart titled *"Inference Speed by Model"*. Task performed: **VQA with a verifiable ground truth.**

**Question:** "Look at this bar chart. Which model is the fastest, and exactly how many tokens per second does it reach?" **Ground truth (I can read it):** Qwen2.5 0.5B, at **98** tok/s.

| System | Answer (short) | Speed | Cost |
| --- | --- | --- | --- |
| Local VLM `moondream` (1.6B, Q4_0) | `"llorma"` — 3-token gibberish, **wrong** | \~49 s wall (1.1 tok/s gen), 1.2 GB | free / local |
| Local VLM `llava:7b` (7B, Q4_0) | "Hana3 … 85.4 tokens per second" — fluent but **hallucinated** (no such model; wrong number) | \~21 s wall (19.4 tok/s gen), 4.8 GB (spilled to CPU) | free / local |
| Gemini (multimodal, hosted) | *not run — no API key* | n/a | free tier |

**Comparison (2–3 sentences):**

> Neither local VLM got it right. `moondream` collapsed completely — it emitted three nonsense tokens (`"llorma"`) and burned \~49 s mostly on image encoding; `llava:7b` was far more *fluent* (it correctly recognized "a bar chart about inference speed by model") but **confidently hallucinated** a non-existent model "Hana3" and an invented value of 85.4 tok/s. On cost both are free and private; on speed `llava` was \~2× faster wall-clock despite being 4× bigger (moondream's tiny size didn't help here). The real lesson is quality: small local VLMs read the *gist* of an image but fail precise chart-text VQA, which is exactly where a larger hosted model (Gemini) would be expected to win — that accuracy gap is the price you pay for going local.