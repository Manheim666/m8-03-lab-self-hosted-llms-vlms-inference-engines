import sys, json, urllib.request

MODEL = sys.argv[1]
PROMPT = ("Explain what an inference engine is and why someone would self-host "
          "one instead of using a hosted API. Answer in about 4 sentences.")

req = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=json.dumps({"model": MODEL, "stream": False,
                     "messages": [{"role": "user", "content": PROMPT}]}).encode(),
    headers={"Content-Type": "application/json"},
)
d = json.load(urllib.request.urlopen(req))
load = d["load_duration"] / 1e9
ec, ed = d["eval_count"], d["eval_duration"] / 1e9
pc = d.get("prompt_eval_count", 0)
tot = d["total_duration"] / 1e9
print(f"MODEL={d['model']}")
print(f"load_s={load:.2f}")
print(f"total_s={tot:.2f}")
print(f"prompt_tokens={pc} gen_tokens={ec}")
print(f"tok_per_s={ec/ed:.1f}")
print("ANSWER:", d["message"]["content"])
