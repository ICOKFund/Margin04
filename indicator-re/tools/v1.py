import sys; sys.path.insert(0, sys.argv[1])
from bn import *
D = load(sys.argv[2]); H4 = load(sys.argv[3])
print("daily bars", len(D), ts(D[0][0]), "->", ts(D[-1][0]))
print("4h bars", len(H4), ts(H4[0][0]), "->", ts(H4[-1][0]))
d = cut(D, ms(2023,4,17), last=(30286.6, 30307.4, 29714.1, 29835.3))
print("--- daily, last 26 bars (as of screenshot)")
for b in d[-26:]:
    print(ts(b[0])[:10], "O %.1f H %.1f L %.1f C %.1f" % b[1:5])
h = cut(H4, ms(2023,4,17,8), last=(29831.2, 29913.6, 29781.6, 29835.1))
print("--- 4h, last 14 bars")
for b in h[-14:]:
    print(ts(b[0]), "O %.1f H %.1f L %.1f C %.1f" % b[1:5])
