"""GitHub Action body: POST each Pine file to the Pine Check API and turn findings into workflow annotations."""
import glob
import json
import os
import sys
import urllib.error
import urllib.request

files = sorted(set(glob.glob(os.environ.get("PC_FILES") or "**/*.pine", recursive=True)))
mode = "lint" if os.environ.get("PC_MODE") == "lint" else "integrity"
fail_on = os.environ.get("PC_FAIL_ON") or "error"
url = (os.environ.get("PC_ENDPOINT") or "https://pine.pokt-agent.com").rstrip("/") + "/v1/" + mode
headers = {"content-type": "application/json", "user-agent": "pine-check-action/0.1"}
if os.environ.get("PC_KEY"):
    headers["Authorization"] = "Bearer " + os.environ["PC_KEY"]
if not files:
    print("::notice::Pine Check: no files matched %s" % os.environ.get("PC_FILES"))
    sys.exit(0)
worst, rank = "CLEAN", {"CLEAN": 0, "WARN": 1, "FAIL": 2}
for path in files:
    src = open(path, encoding="utf-8", errors="replace").read()
    req = urllib.request.Request(url, data=json.dumps({"source": src}).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            res = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        print("::warning file=%s::Pine Check could not check this file (HTTP %d): %s" % (path, e.code, body))
        continue
    for f in res.get("findings", []):
        level = {"error": "error", "warning": "warning"}.get(f["severity"], "notice")
        print("::%s file=%s,line=%s,title=%s::%s" % (level, path, f.get("line") or 1, f["code"], f["message"].replace("\n", " ")))
    print("%s: %s %s" % (path, res.get("verdict"), json.dumps(res.get("counts"))))
    if rank.get(res.get("verdict"), 0) > rank[worst]:
        worst = res.get("verdict")
limit = {"error": 2, "warning": 1, "never": 3}.get(fail_on, 2)
print("Pine Check: worst verdict %s over %d file(s); checks are static and say nothing about profitability." % (worst, len(files)))
sys.exit(1 if rank[worst] >= limit else 0)
