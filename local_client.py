"""
Task 2 — Hit the local Ollama endpoint from Python.

Ollama exposes an OpenAI-compatible HTTP API on http://localhost:11434.
That means the SAME client code you used for a hosted API works here —
you only change the base URL (and the API key is a dummy value locally).

Run Ollama first (it starts a server automatically when you `ollama run`
or `ollama serve`), then:

    pip install -r requirements.txt
    python local_client.py
"""

from openai import OpenAI

# Point the OpenAI client at your LOCAL Ollama server instead of the cloud.
# This is the whole insight of the lab: "calling an LLM" is just an HTTP
# request to an inference server — wherever that server happens to run.
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client, but ignored by Ollama
)

MODEL = "llama3.2:3b"  # any model you pulled with `ollama pull`


def main() -> None:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "In one sentence, what is an inference engine?"},
        ],
    )
    print(response.choices[0].message.content)


# -----------------------------------------------------------------------------
# Reflection — why is this "the same shape" as yesterday's hosted Gemini call?
#
# Yesterday's hosted call and this local call are the *same request shape*:
#
#   1. Both are just HTTP POSTs to a /chat/completions-style endpoint. The only
#      thing that changed is the `base_url`: Gemini pointed at Google's servers,
#      this points at http://localhost:11434 — my own laptop. The transport
#      (HTTP + JSON) is identical.
#   2. The request body is the same schema: a `model` string and a `messages`
#      list of {role, content} objects (system / user / assistant). The response
#      comes back in the same envelope: choices[0].message.content.
#   3. The exact same `openai` SDK object talks to both. I didn't swap libraries
#      — I swapped a URL and a (here meaningless) API key. Ollama deliberately
#      mimics the OpenAI API so existing tooling "just works".
#
# The lesson: an LLM is not magic living in a special cloud. It's a process
# listening on a socket that takes text in and streams tokens out. Hosted vs.
# self-hosted is only a question of *which machine* runs that process — the
# contract my code speaks to is the same either way. That's why I can move from
# a paid hosted API to a free local one by editing one line.
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
