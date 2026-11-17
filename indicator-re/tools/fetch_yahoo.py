import sys, json, urllib.request, urllib.parse, urllib.error
sym, out = sys.argv[1], sys.argv[2]
p1, p2 = sys.argv[3], sys.argv[4]
interval = sys.argv[5] if len(sys.argv) > 5 else "1d"
url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%s&period2=%s&interval=%s&events=div%%2Csplit" % (urllib.parse.quote(sym), p1, p2, interval)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read()[:200]); sys.exit(1)
j = json.loads(data)
res = j["chart"]["result"][0]
ts = res["timestamp"]; q = res["indicators"]["quote"][0]
rows = []
for i, t in enumerate(ts):
    o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
    if None in (o, h, l, c): continue
    rows.append((t, o, h, l, c, v or 0))
with open(out, "w") as f:
    f.write("time,open,high,low,close,volume\n")
    for r in rows: f.write("%d,%.6f,%.6f,%.6f,%.6f,%d\n" % r)
import datetime as dt
print(sym, len(rows), dt.datetime.utcfromtimestamp(rows[0][0]).date(), "->", dt.datetime.utcfromtimestamp(rows[-1][0]).date(), "tz", res["meta"].get("exchangeTimezoneName"))
