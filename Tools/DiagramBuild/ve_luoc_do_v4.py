# -*- coding: utf-8 -*-
"""Vẽ sơ đồ quan hệ FitLife Hub từ schema.py.
  python ve_luoc_do_v4.py            -> 4 file PNG (tổng + 3 mô-đun) + ve_ket_qua.json + .drawio
Định tuyến vuông góc bằng A* trên lưới (kế thừa ve_luoc_do.py, đã gọn lại thành hàm).
"""
import heapq
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.patches import Rectangle, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import TABLES, FKS, GROUPS, MODULES  # noqa: E402
from layouts import LAYOUTS  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
COL = {"dm": "#2f6ea8", "hv": "#2e8b57", "goi": "#c8691c", "sp": "#5b4ea0", "ns": "#b8324f", "vh": "#16898a"}
FONT = FontProperties(family="DejaVu Sans")
FONT_B = FontProperties(family="DejaVu Sans", weight="bold")
G = 6
CELL_H = 24
FS = 8.5
PT2PX = 100 / 72
DPI = 200


def tw(s, bold=False, size=FS):
    return TextPath((0, 0), s, size=size, prop=FONT_B if bold else FONT).get_extents().width * PT2PX


def snap(v):
    return int(round(v / G)) * G


def lighten(hex_, f=0.55):
    r, g, b = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    r, g, b = [int(c + (255 - c) * f) for c in (r, g, b)]
    return "#%02x%02x%02x" % (r, g, b)


def label(tb, col):
    for n, _t, _nn, fl in TABLES[tb]["cols"]:
        if n == col:
            s = "[%s]" % n if "D" in fl else n
            return s + (" ◆" if "U" in fl else "")
    raise KeyError((tb, col))


def kind_of(fl):
    return "pkfk" if ("P" in fl and "F" in fl) else "pk" if "P" in fl else "fk" if "F" in fl else ""


def render(key, spec, draw=True):
    layout = spec["rows"]          # list[list[(name, x|None)]]
    ghosts = set(spec.get("ghosts", []))
    W = spec["W"]
    ROW_GAP = spec.get("row_gap", 120)
    ROW_Y0 = 90
    nrows = len(layout)
    names = [n for r in layout for n, _ in r]
    inside = [n for n in names if n not in ghosts]
    fks = [f for f in FKS if f[0] in inside and f[2] in names]
    H = ROW_Y0 + (nrows - 1) * ROW_GAP + CELL_H + 70 + 5 * 24 + 40

    incoming = {}
    for s, fc, t, pc, _ in fks:
        for c in pc:
            incoming[(t, c)] = incoming.get((t, c), 0) + 1

    tables = {}
    for ri, row in enumerate(layout):
        cx_auto = 40
        for name, xfix in row:
            T = TABLES[name]
            ghost = name in ghosts
            cols = [(n, fl) for n, _t, _nn, fl in T["cols"] if (not ghost or "P" in fl)]
            name_w = snap(tw(name, True) + 18)
            x = xfix if xfix is not None else cx_auto
            cells, order, cx = {}, [], x + name_w
            for n, fl in cols:
                w = tw(label(name, n)) + 16
                w = snap(max(w, (incoming.get((name, n), 0) + 1) * 8) + G / 2)
                cells[n] = (cx, cx + w, "pk" if ghost and "P" in fl else kind_of(fl))
                order.append(n)
                cx += w
            y = ROW_Y0 + ri * ROW_GAP
            tables[name] = dict(grp=T["grp"], x0=x, x1=cx, y0=y, y1=y + CELL_H, name_w=name_w,
                                cells=cells, order=order, ghost=ghost)
            cx_auto = cx + spec.get("gap", 60)
    maxx = max(T["x1"] for T in tables.values())
    if maxx > W - 30:
        raise RuntimeError("%s: bảng rộng quá, cần W >= %d" % (key, maxx + 30))

    # ------------------------------------------------ cổng nối
    ends, port_req = [], {}
    for i, (s, fc, t, pc, _r) in enumerate(fks):
        S, T = tables[s], tables[t]
        if S["y0"] > T["y0"]:
            ss, ts = -1, +1
        elif S["y0"] < T["y0"]:
            ss, ts = +1, -1
        else:
            ss, ts = +1, +1
        sx = np.mean([sum(S["cells"][c][:2]) / 2 for c in fc])
        txx = np.mean([sum(T["cells"][c][:2]) / 2 for c in pc])
        ends.append(dict(s=s, fc=fc, ss=ss, t=t, pc=pc, ts=ts))
        port_req.setdefault((s, tuple(fc), ss), []).append((i, "s", txx))
        port_req.setdefault((t, tuple(pc), ts), []).append((i, "t", sx))
    for (tb, cols, side), lst in port_req.items():
        T = tables[tb]
        x0, x1 = T["cells"][cols[0]][0], T["cells"][cols[-1]][1]
        if len(cols) > 1:
            xs = [snap((x0 + x1) / 2)]
        else:
            n = len(lst)
            xs = [snap(x0 + (x1 - x0) * (k + 1) / (n + 1)) for k in range(n)]
            for k in range(1, n):
                if xs[k] <= xs[k - 1]:
                    xs[k] = xs[k - 1] + G
        lst.sort(key=lambda r: r[2])
        for k, (i, role, _) in enumerate(lst):
            ends[i][role + "x"] = xs[min(k, len(xs) - 1)]

    # ------------------------------------------------ lưới
    NX, NY = W // G + 1, H // G + 1
    blocked = np.zeros((NY, NX), bool)
    for T in tables.values():
        gx0 = max(0, (T["x0"] - G) // G)
        gx1 = min(NX - 1, (T["x1"] + G) // G + 1)
        gy0 = max(0, (T["y0"] - G) // G)
        gy1 = min(NY - 1, (T["y1"] + G) // G + 1)
        blocked[gy0:gy1 + 1, gx0:gx1] = True
    blocked[:, :2] = True
    blocked[:, -2:] = True
    blocked[: (ROW_Y0 - 30) // G, :] = True
    blocked[(ROW_Y0 + (nrows - 1) * ROW_GAP + CELL_H + 44) // G:, :] = True
    usedH = np.zeros((NY, NX), np.int16)
    usedV = np.zeros((NY, NX), np.int16)
    portcell = np.zeros((NY, NX), bool)

    def endpoint(tb, side, x):
        T = tables[tb]
        ey = T["y0"] if side < 0 else T["y1"]
        gy = (snap(ey) // G) + side * 2
        while blocked[gy, x // G]:
            gy += side
        return (x // G, gy), ey

    for e in ends:
        e["sg"], e["sy"] = endpoint(e["s"], e["ss"], e["sx"])
        e["tg"], e["ty"] = endpoint(e["t"], e["ts"], e["tx"])
        for (gx, gy), ey, side in ((e["sg"], e["sy"], e["ss"]), (e["tg"], e["ty"], e["ts"])):
            y = gy
            while (y * G - ey) * side > 0:
                portcell[y, gx] = True
                y -= side
            portcell[gy, gx] = True

    DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    BEND, OVER, CROSS, NEAR, COLL = 16, 80, 20, 4, 60
    corner = np.zeros((NY, NX), bool)

    def route(e):
        (sx, sy), (tx, ty) = e["sg"], e["tg"]
        own = {(sx, sy), (tx, ty)}
        start_dir = 2 if e["ss"] > 0 else 3
        end_dir = 3 if e["ts"] > 0 else 2
        INF = 1 << 30
        best, parent = {}, {}
        pq = [(abs(sx - tx) + abs(sy - ty), 0, sx, sy, start_dir, None)]
        key_ = None
        while pq:
            f, g, x, y, d, par = heapq.heappop(pq)
            k = (x, y, d)
            if k in parent:
                continue
            parent[k] = par
            if (x, y) == (tx, ty):
                if d == end_dir:
                    key_ = k
                    break
                continue
            for nd, (dx, dy) in enumerate(DIRS):
                if (nd ^ 1) == d and nd // 2 == d // 2 and nd != d:
                    continue
                nx_, ny_ = x + dx, y + dy
                if not (0 <= nx_ < NX and 0 <= ny_ < NY) or blocked[ny_, nx_]:
                    continue
                if portcell[ny_, nx_] and (nx_, ny_) not in own:
                    continue
                c = 1 + (BEND if nd != d else 0) + (OVER if corner[ny_, nx_] else 0)
                if dx:
                    if corner[ny_, max(nx_ - 2, 0):nx_ + 3].any():
                        c += COLL
                    if usedH[ny_, nx_]:
                        c += OVER
                    if usedV[ny_, nx_]:
                        c += CROSS
                    if (ny_ > 0 and usedH[ny_ - 1, nx_]) or (ny_ + 1 < NY and usedH[ny_ + 1, nx_]):
                        c += NEAR
                else:
                    if corner[max(ny_ - 2, 0):ny_ + 3, nx_].any():
                        c += COLL
                    if usedV[ny_, nx_]:
                        c += OVER
                    if usedH[ny_, nx_]:
                        c += CROSS
                    if (nx_ > 0 and usedV[ny_, nx_ - 1]) or (nx_ + 1 < NX and usedV[ny_, nx_ + 1]):
                        c += NEAR
                ng = g + c
                nk = (nx_, ny_, nd)
                if best.get(nk, INF) <= ng:
                    continue
                best[nk] = ng
                heapq.heappush(pq, (ng + abs(nx_ - tx) + abs(ny_ - ty), ng, nx_, ny_, nd, k))
        if key_ is None:
            raise RuntimeError("không tìm được đường cho %s -> %s" % (e["s"], e["t"]))
        path, k = [], key_
        while k is not None:
            path.append(k)
            k = parent[k]
        path.reverse()
        for i in range(1, len(path)):
            x, y, d = path[i]
            (usedH if d < 2 else usedV)[y, x] += 1
        for i in range(len(path)):
            x, y, d = path[i]
            if i == 0 or i == len(path) - 1 or path[i + 1][2] != d:
                corner[y, x] = True
        return [(x * G, y * G) for x, y, _ in path]

    order = sorted(range(len(ends)), key=lambda i: -(abs(ends[i]["sg"][0] - ends[i]["tg"][0])
                                                      + abs(ends[i]["sg"][1] - ends[i]["tg"][1])))
    for i in order:
        ends[i]["pts"] = route(ends[i])

    def simplify(pts):
        out = [pts[0]]
        for p in pts[1:]:
            if len(out) >= 2:
                a, b = out[-2], out[-1]
                if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                    out[-1] = p
                    continue
            if p != out[-1]:
                out.append(p)
        return out

    def path_cells(pts):
        cells = {}
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            o = "H" if y0 == y1 else "V"
            n = abs(x1 - x0) + abs(y1 - y0)
            sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
            for k in range(n + 1):
                c = (x0 + sx * k, y0 + sy * k)
                cells[c] = "C" if c in cells and cells[c] != o else o
        for c in (pts[0], pts[-1], *pts[1:-1]):
            cells[c] = "C"
        return cells

    def straighten():
        gp = [simplify([(x // G, y // G) for x, y in e["pts"]]) for e in ends]
        cs = [path_cells(p) for p in gp]

        def free(i, cells):
            own = {gp[i][0], gp[i][-1]}
            for c, o in cells.items():
                x, y = c
                if blocked[y, x] or (portcell[y, x] and c not in own):
                    return False
                for j in range(len(gp)):
                    if j != i and c in cs[j]:
                        oj = cs[j][c]
                        if oj == "C" or o == "C" or oj == o:
                            return False
            return True

        changed = True
        while changed:
            changed = False
            for i, p in enumerate(gp):
                for k in range(len(p) - 3):
                    p0, p1, p2, p3 = p[k:k + 4]
                    if abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) > 3:
                        continue
                    vert = p0[0] == p1[0] and p2[0] == p3[0]
                    horz = p0[1] == p1[1] and p2[1] == p3[1]
                    if not (vert or horz):
                        continue
                    cands = []
                    if k + 3 < len(p) - 1:
                        q3 = (p1[0], p3[1]) if vert else (p3[0], p1[1])
                        cands.append(p[:k + 1] + [q3] + p[k + 4:])
                    if k > 0:
                        q0 = (p2[0], p0[1]) if vert else (p0[0], p2[1])
                        cands.append(p[:k] + [q0] + p[k + 3:])
                    for cand in cands:
                        cand = simplify(cand)
                        cells = path_cells(cand)
                        if free(i, cells):
                            gp[i], cs[i] = cand, cells
                            changed = True
                            break
                    if changed:
                        break
        for e, p in zip(ends, gp):
            e["pts"] = [(x * G, y * G) for x, y in p]

    straighten()
    if not draw:
        cross = int(((usedH > 0) & (usedV > 0)).sum())
        bends = sum(len(simplify(e["pts"])) - 2 for e in ends)
        return dict(crossings=cross, bends=bends, length=int((usedH + usedV).sum())), tables

    # ------------------------------------------------ vẽ
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(W / 2, 32, spec["title"], ha="center", va="center", fontsize=15,
            fontproperties=FONT_B, color="#222")
    LW, COMP = 1.15, 8
    out = dict(key=key, W=W, H=H, png=spec["png"], tables={}, edges=[])

    def dashed(x0, x1, y, dash=5.0, gap=3.0, **kw):
        n = max(1, int(round((x1 - x0 + gap) / (dash + gap))))
        dash = (x1 - x0 - (n - 1) * gap) / n
        for k in range(n):
            a = x0 + k * (dash + gap)
            ax.plot([a, a + dash], [y, y], solid_capstyle="butt", **kw)

    def arrow_head(x, y, side, color):
        Ln, Wd = 7, 3.6
        ax.add_patch(Polygon([(x, y), (x - Wd, y + side * Ln), (x + Wd, y + side * Ln)], closed=True,
                             color=color, zorder=5, lw=0))

    for e in ends:
        S = tables[e["s"]]
        color = COL[S["grp"]]
        pts = simplify(e["pts"])
        comp = len(e["fc"]) > 1
        sy_edge = e["sy"] + (e["ss"] * COMP if comp else 0)
        ty_edge = e["ty"] + (e["ts"] * (COMP + 7) if comp else 0)
        full = simplify([(e["sx"], sy_edge)] + pts + [(e["tx"], ty_edge)])
        xs, ys = zip(*full)
        ax.plot(xs, ys, color=color, lw=LW, zorder=3, solid_joinstyle="miter")
        heads = []
        if comp:
            cxs = [sum(S["cells"][c][:2]) / 2 for c in e["fc"]]
            yb = e["sy"] + e["ss"] * COMP
            for cx in cxs:
                ax.plot([cx, cx], [e["sy"], yb], color=color, lw=LW, zorder=3)
            ax.plot([min(cxs), max(cxs)], [yb, yb], color=color, lw=LW, zorder=3)
            ax.plot([e["sx"]], [yb], marker="o", ms=3.2, color=color, zorder=4)
            T = tables[e["t"]]
            txs = [sum(T["cells"][c][:2]) / 2 for c in e["pc"]]
            yb2 = e["ty"] + e["ts"] * (COMP + 7)
            ax.plot([min(txs), max(txs)], [yb2, yb2], color=color, lw=LW, zorder=3)
            ax.plot([e["tx"]], [yb2], marker="o", ms=3.2, color=color, zorder=4)
            for cx in txs:
                ax.plot([cx, cx], [yb2, e["ty"] + e["ts"] * 7], color=color, lw=LW, zorder=3)
                arrow_head(cx, e["ty"], e["ts"], color)
                heads.append([cx, e["ty"]])
            starts = [[cx, e["sy"]] for cx in cxs]
        else:
            arrow_head(e["tx"], e["ty"], e["ts"], color)
            heads.append([e["tx"], e["ty"]])
            starts = [[e["sx"], e["sy"]]]
        e["full"] = full
        out["edges"].append(dict(src=e["s"], fc=e["fc"], dst=e["t"], pc=e["pc"], starts=starts,
                                 heads=heads, path=[list(p) for p in full], color=color))

    for name, T in tables.items():
        c = COL[T["grp"]]
        ec = c
        fc_name = lighten(c, 0.0) if not T["ghost"] else lighten(c, 0.6)
        y0, y1 = T["y0"], T["y1"]
        ax.add_patch(Rectangle((T["x0"], y0), T["name_w"], CELL_H, facecolor=fc_name, edgecolor=ec,
                               lw=1.2, zorder=6, ls=(0, (3, 2)) if T["ghost"] else "-"))
        ax.text(T["x0"] + T["name_w"] / 2, (y0 + y1) / 2, name, ha="center", va="center", fontsize=FS,
                fontproperties=FONT_B, color="white" if not T["ghost"] else "#444", zorder=7)
        cells_out = []
        for a in T["order"]:
            cx0, cx1, kind = T["cells"][a]
            ax.add_patch(Rectangle((cx0, y0), cx1 - cx0, CELL_H, facecolor="#f6f6f6" if T["ghost"] else "white",
                                   edgecolor=ec, lw=1.2, zorder=6, ls=(0, (3, 2)) if T["ghost"] else "-"))
            lab = label(name, a)
            mid = (cx0 + cx1) / 2
            ax.text(mid, (y0 + y1) / 2 - 1, lab, ha="center", va="center", fontsize=FS, fontproperties=FONT,
                    color="#1a1a1a" if not T["ghost"] else "#555", zorder=7)
            wf, wn = tw(lab), tw(lab.split(" ◆")[0])
            ux0, ux1 = mid - wf / 2, mid - wf / 2 + wn
            if kind in ("pk", "pkfk"):
                ax.plot([ux0, ux1], [y1 - 5, y1 - 5], color="#1a1a1a", lw=0.9, zorder=7)
            if kind == "fk":
                dashed(ux0, ux1, y1 - 5, color="#1a1a1a", lw=0.9, zorder=7)
            if kind == "pkfk":
                dashed(ux0, ux1, y1 - 2.5, color="#1a1a1a", lw=0.9, zorder=7)
            cells_out.append(dict(col=a, x0=cx0, x1=cx1, kind=kind))
        out["tables"][name] = dict(x0=T["x0"], x1=T["x1"], y0=y0, y1=y1, ghost=T["ghost"],
                                   name_w=T["name_w"], cells=cells_out)
        if T["ghost"]:
            ax.text(T["x0"], y1 + 9 if True else y0 - 8, "(bảng ở mô-đun khác – chỉ hiện khóa chính)",
                    fontsize=6.6, fontproperties=FONT, color="#777", va="center", zorder=7)

    # ---------------- chú giải
    ly = ROW_Y0 + (nrows - 1) * ROW_GAP + CELL_H + 70
    lx = 40
    ax.text(lx, ly, "Chú giải", fontsize=9.5, fontproperties=FONT_B, va="center", color="#222")
    ly += 24
    fs = 8.3

    def leg_text(x, y, s):
        ax.text(x, y, s, fontsize=fs, fontproperties=FONT, va="center", color="#222")
        return x + tw(s, size=fs)

    x = lx
    ax.plot([x, x + 34], [ly + 4, ly + 4], color="#1a1a1a", lw=0.9)
    x = leg_text(x + 42, ly, "Gạch chân liền: khóa chính") + 34
    dashed(x, x + 34, ly + 4, color="#1a1a1a", lw=0.9)
    x = leg_text(x + 42, ly, "Gạch chân đứt: khóa ngoại") + 34
    ax.plot([x, x + 34], [ly + 2, ly + 2], color="#1a1a1a", lw=0.9)
    dashed(x, x + 34, ly + 5.5, color="#1a1a1a", lw=0.9)
    x = leg_text(x + 42, ly, "Liền + đứt: vừa là khóa chính vừa là khóa ngoại") + 34
    x = leg_text(x, ly, "◆  khóa thay thế / có ràng buộc UNIQUE") + 34
    x = leg_text(x, ly, "[Tên]  thuộc tính dẫn xuất nhưng có lưu (E5)")
    ly += 24
    x = lx
    ax.plot([x, x + 30], [ly, ly], color="#444", lw=LW)
    ax.add_patch(Polygon([(x + 37, ly), (x + 30, ly - 3.6), (x + 30, ly + 3.6)], color="#444", lw=0))
    x = leg_text(x + 46, ly, "Mũi tên: từ khóa ngoại đến khóa chính được tham chiếu (màu theo phân hệ của bảng chứa khóa ngoại)") + 34
    bx = x
    ax.plot([bx, bx], [ly - 7, ly], color="#444", lw=LW)
    ax.plot([bx + 16, bx + 16], [ly - 7, ly], color="#444", lw=LW)
    ax.plot([bx, bx + 16], [ly, ly], color="#444", lw=LW)
    ax.plot([bx + 8, bx + 8, bx + 30], [ly, ly + 6, ly + 6], color="#444", lw=LW)
    ax.plot([bx + 8], [ly], marker="o", ms=3.2, color="#444")
    leg_text(bx + 40, ly, "Hai cột gộp vào một đường: khóa ngoại ghép")
    ly += 24
    x = lx
    groups_here = []
    for n in inside:
        g = TABLES[n]["grp"]
        if g not in groups_here:
            groups_here.append(g)
    for g in groups_here:
        ax.add_patch(Rectangle((x, ly - 6), 12, 12, facecolor=COL[g], edgecolor=COL[g]))
        x = leg_text(x + 18, ly, GROUPS[g]) + 30
    if ghosts:
        ax.add_patch(Rectangle((x, ly - 6), 12, 12, facecolor="#f6f6f6", edgecolor="#888", ls=(0, (3, 2))))
        leg_text(x + 18, ly, "Bảng nét đứt, màu nhạt: thuộc mô-đun khác")
    ly += 24
    ax.text(lx, ly, spec["note"], fontsize=8, fontproperties=FONT, va="center", color="#555")

    fig.savefig(os.path.join(HERE, spec["png"]), dpi=DPI, facecolor="white")
    plt.close(fig)
    cross = int(((usedH > 0) & (usedV > 0)).sum())
    bends = sum(len(simplify(e["pts"])) - 2 for e in ends)
    out.update(crossings=cross, bends=bends, length=int((usedH + usedV).sum()))
    print("%-4s %d bảng, %d mũi tên, giao cắt~%d, khúc~%d, ảnh %dx%d" %
          (key, len(tables), len(ends), cross, bends, W * DPI // 100, H * DPI // 100))
    return out, tables


def drawio(figs):
    """Xuất .drawio: mỗi hình một trang; bảng = ô tên + ô cột, mũi tên nối ô FK -> ô PK."""
    from xml.sax.saxutils import quoteattr
    parts = ['<mxfile host="app.diagrams.net">']
    for fi, (out, tables) in enumerate(figs):
        cid = [1]
        ids = {}

        def nid():
            cid[0] += 1
            return "c%d_%d" % (fi, cid[0])
        cells = []
        for name, T in tables.items():
            c = COL[T["grp"]]
            fill = c if not T["ghost"] else lighten(c, 0.6)
            i = nid()
            ids[(name, None)] = i
            cells.append('<mxCell id="%s" value=%s style="rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;'
                         'fontColor=%s;fontStyle=1;fontSize=11;%s" vertex="1" parent="1"><mxGeometry x="%d" y="%d" '
                         'width="%d" height="%d" as="geometry"/></mxCell>' %
                         (i, quoteattr(name), fill, c, "#ffffff" if not T["ghost"] else "#444444",
                          "dashed=1;" if T["ghost"] else "", T["x0"], T["y0"], T["name_w"], CELL_H))
            for a in T["order"]:
                x0, x1, kind = T["cells"][a]
                lab = label(name, a)
                if kind in ("pk", "pkfk"):
                    html = "<u>%s</u>" % lab
                elif kind == "fk":
                    html = '<u style="text-decoration-style:dashed">%s</u>' % lab
                else:
                    html = lab
                i = nid()
                ids[(name, a)] = i
                cells.append('<mxCell id="%s" value=%s style="rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=%s;'
                             'fontSize=10;%s" vertex="1" parent="1"><mxGeometry x="%d" y="%d" width="%d" height="%d" '
                             'as="geometry"/></mxCell>' %
                             (i, quoteattr(html), "#f6f6f6" if T["ghost"] else "#ffffff", c,
                              "dashed=1;" if T["ghost"] else "", x0, T["y0"], x1 - x0, CELL_H))
        for ed in out["edges"]:
            S, Tt = tables[ed["src"]], tables[ed["dst"]]
            sc, tc = ed["fc"][0], ed["pc"][0]
            sx0, sx1, _ = S["cells"][sc]
            tx0, tx1, _ = Tt["cells"][tc]
            p0, p1 = ed["path"][0], ed["path"][-1]
            ey = 0 if p0[1] <= S["y0"] else 1
            ty = 0 if p1[1] <= Tt["y0"] else 1
            exf = min(max((p0[0] - sx0) / (sx1 - sx0), 0), 1)
            enf = min(max((p1[0] - tx0) / (tx1 - tx0), 0), 1)
            pts = "".join('<mxPoint x="%d" y="%d"/>' % tuple(p) for p in ed["path"][1:-1])
            i = nid()
            val = "(" + ", ".join(ed["fc"]) + ")" if len(ed["fc"]) > 1 else ""
            cells.append('<mxCell id="%s" value=%s style="endArrow=block;endFill=1;html=1;rounded=0;strokeColor=%s;'
                         'exitX=%.3f;exitY=%d;exitDx=0;exitDy=0;entryX=%.3f;entryY=%d;entryDx=0;entryDy=0;" edge="1" '
                         'parent="1" source="%s" target="%s"><mxGeometry relative="1" as="geometry"><Array as="points">%s'
                         '</Array></mxGeometry></mxCell>' %
                         (i, quoteattr(val), ed["color"], exf, ey, enf, ty, ids[(ed["src"], sc)],
                          ids[(ed["dst"], tc)], pts))
        parts.append('<diagram id="d%d" name="%s"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="6" page="1" '
                     'pageWidth="%d" pageHeight="%d"><root><mxCell id="0"/><mxCell id="1" parent="0"/>%s</root>'
                     '</mxGraphModel></diagram>' % (fi, out["key"], out["W"], out["H"], "".join(cells)))
    parts.append("</mxfile>")
    with open(os.path.join(HERE, "luoc_do_quan_he_v4.drawio"), "w", encoding="utf-8") as f:
        f.write("".join(parts))


if __name__ == "__main__":
    only = sys.argv[1:] or list(LAYOUTS)
    figs = []
    for k in only:
        figs.append(render(k, LAYOUTS[k]))
    if not sys.argv[1:]:
        drawio(figs)
        with open(os.path.join(HERE, "ve_ket_qua.json"), "w", encoding="utf-8") as f:
            json.dump({o["key"]: o for o, _ in figs}, f, ensure_ascii=False)
        print("đã ghi ve_ket_qua.json và .drawio")
