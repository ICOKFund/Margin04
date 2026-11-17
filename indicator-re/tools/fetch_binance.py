import sys, os, urllib.request, urllib.error, time
sym, tf, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
y0, m0, y1, m1 = [int(v) for v in sys.argv[4:8]]
ok = miss = 0
y, m = y0, m0
while (y, m) <= (y1, m1):
    name = f"{sym}-{tf}-{y}-{m:02d}.zip"
    url = f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/{tf}/{name}"
    dst = os.path.join(outdir, name)
    if not os.path.exists(dst):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            with open(dst, "wb") as f:
                f.write(data)
            ok += 1
        except urllib.error.HTTPError as e:
            miss += 1; print("  miss", name, e.code)
        except Exception as e:
            miss += 1; print("  err", name, repr(e)[:120])
        time.sleep(0.05)
    else:
        ok += 1
    m += 1
    if m == 13: y, m = y + 1, 1
print(f"{sym} {tf}: ok={ok} miss={miss}")
