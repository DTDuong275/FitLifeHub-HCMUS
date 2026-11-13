# -*- coding: utf-8 -*-
"""Leo đồi trên bố cục có tọa độ x tường minh, chấm bằng đúng lưới vẽ thật (G=6).
  python tim_bo_cuc2.py <hình> <số vòng>   -> ghi best2_<hình>.json (rows: [[tên, x], ...] theo hàng)
Xuất phát từ layouts.LAYOUTS[hình]; mỗi vòng chấm 12 ứng viên song song.
"""
import json
import os
import random
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ve_luoc_do_v4 as V  # noqa: E402
from layouts import LAYOUTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WIDTH = {}
KEY = None


def init_worker(w, key):
    WIDTH.update(w)
    globals()["KEY"] = key


def fits(row, W):
    xs = sorted((x, WIDTH[n]) for n, x in row)
    if not xs:
        return True
    if xs[0][0] < 30 or xs[-1][0] + xs[-1][1] > W - 30:
        return False
    return all(a[0] + a[1] + 8 <= b[0] for a, b in zip(xs, xs[1:]))


def score(rows):
    sp = dict(LAYOUTS[KEY])
    sp["rows"] = [[(n, x) for n, x in r] for r in rows]
    try:
        m, _ = V.render(KEY, sp, draw=False)
    except Exception:
        return 1e9
    return 10 * m["crossings"] + m["bends"] + m["length"] / 30


def mutate(rows, rng, W):
    rows = [[list(t) for t in r] for r in rows]
    for _ in range(30):
        t = rng.random()
        ri = rng.randrange(len(rows))
        if not rows[ri]:
            continue
        k = rng.randrange(len(rows[ri]))
        if t < 0.45:                                  # dời ngang
            rows[ri][k][1] += rng.choice([-320, -160, -80, -40, 40, 80, 160, 320])
        elif t < 0.8:                                 # chuyển sang hàng khác, x ngẫu nhiên
            rj = rng.randrange(len(rows))
            if rj == ri:
                continue
            n = rows[ri].pop(k)[0]
            rows[rj].append([n, 40 * rng.randrange(1, (W - 300) // 40)])
            ri = rj
        else:                                         # đổi chỗ hai bảng (giữ x nguồn)
            rj = rng.randrange(len(rows))
            if not rows[rj] or rj == ri:
                continue
            k2 = rng.randrange(len(rows[rj]))
            rows[ri][k][0], rows[rj][k2][0] = rows[rj][k2][0], rows[ri][k][0]
        if all(fits([tuple(t) for t in r], W) for r in rows):
            return [[tuple(t) for t in r] for r in rows if r]
        rows = [[list(t) for t in r] for r in rows]
    return None


if __name__ == "__main__":
    key = sys.argv[1]
    iters = int(sys.argv[2])
    KEY = key
    base = LAYOUTS[key]
    probe = dict(base)
    probe["W"] = 5000
    _, tabs = V.render(key, probe, draw=False)
    WIDTH.update({n: t["x1"] - t["x0"] for n, t in tabs.items()})
    rows0 = [[(n, x) for n, x in r] for r in base["rows"]]
    best = (score(rows0), rows0)
    print("khởi đầu", round(best[0], 1), flush=True)
    rng = random.Random(11)
    with Pool(11, initializer=init_worker, initargs=(WIDTH, key)) as pool:
        for it in range(iters):
            cands = [c for c in (mutate(best[1], rng, base["W"]) for _ in range(22)) if c]
            res = sorted(zip(pool.map(score, cands), range(len(cands))), key=lambda r: r[0])
            sc, ci = res[0]
            if sc <= best[0]:
                if sc < best[0]:
                    print("vòng", it, "điểm", round(sc, 1), flush=True)
                best = (sc, cands[ci])
                json.dump(dict(score=sc, rows=[[list(t) for t in r] for r in best[1]]),
                          open(os.path.join(HERE, "best2_%s.json" % key), "w"), ensure_ascii=False)
    print("xong", round(best[0], 1))
