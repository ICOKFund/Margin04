# shared loader for Binance kline archives (run with python3 -I; add tools dir to sys.path manually)
import zipfile, glob, os, datetime as dt
def load(dirpath):
    rows = {}
    for zp in sorted(glob.glob(os.path.join(dirpath, "*.zip"))):
        z = zipfile.ZipFile(zp)
        for line in z.read(z.namelist()[0]).decode().splitlines():
            p = line.split(",")
            if not p[0].isdigit(): continue
            t = int(p[0])
            rows[t] = (t, float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5]))
    out = [rows[k] for k in sorted(rows)]
    return out
def ts(t): return dt.datetime.fromtimestamp(t/1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
def cut(bars, end_ms, last=None):
    """keep bars with open_time <= end_ms; optionally override the last bar's OHLC (developing bar)."""
    b = [x for x in bars if x[0] <= end_ms]
    if last is not None:
        t = b[-1][0]; b[-1] = (t, last[0], last[1], last[2], last[3], b[-1][5])
    return b
def ms(y, m, d, h=0): return int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp()*1000)
