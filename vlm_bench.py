import sys, json, base64, urllib.request

MODEL = sys.argv[1]
IMG = sys.argv[2]
Q = ("Look at this bar chart. Which model is the fastest, and exactly how many "
     "tokens per second does it reach? Answer in one sentence.")

b64 = base64.b64encode(open(IMG, "rb").read()).decode()
req = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=json.dumps({"model": MODEL, "stream": False,
                     "messages": [{"role": "user", "content": Q, "images": [b64]}]}).encode(),
    headers={"Content-Type": "application/json"},
)
d = json.load(urllib.request.urlopen(req))
print(f"MODEL={d['model']}")
print(f"load_s={d['load_duration']/1e9:.2f}")
print(f"total_s={d['total_duration']/1e9:.2f}")
print(f"gen_tokens={d['eval_count']} tok_per_s={d['eval_count']/(d['eval_duration']/1e9):.1f}")
print("ANSWER:", d["message"]["content"].strip())
