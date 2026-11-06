# -*- coding: utf-8 -*-
"""Redraw of the Shum Yip Century Valley 3C 262 sqm (04+05 merged) floor plan.
Units: millimetres. Axis grid taken from the developer's dimension chains;
interior partitions scaled from the source image (tolerance ~ +/-200 mm)."""
import math, cairosvg

FONT = "WenQuanYi Micro Hei, Noto Sans CJK SC, Droid Sans Fallback, sans-serif"
W_EXT, W_INT, W_SHEAR = 250, 200, 400

out = []
def add(s): out.append(s)

# ---------- primitives ----------
def rect(x1, y1, x2, y2, fill="none", stroke="#000", sw=20, extra=""):
    add(f'<rect x="{min(x1,x2)}" y="{min(y1,y2)}" width="{abs(x2-x1)}" height="{abs(y2-y1)}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def line(x1, y1, x2, y2, stroke="#000", sw=20, extra=""):
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def circle(cx, cy, r, fill="none", stroke="#000", sw=20):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def text(x, y, s, size=300, anchor="middle", fill="#000", weight="normal", rotate=0, extra=""):
    tr = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" '
        f'fill="{fill}" font-weight="{weight}"{tr} {extra}>{s}</text>')

def wall(x1, y1, x2, y2, t=W_INT, fill="#2b2b2b"):
    """Wall segment centred on the axis line between (x1,y1)-(x2,y2)."""
    if x1 == x2:
        rect(x1 - t/2, min(y1,y2) - (t/2 if False else 0), x1 + t/2, max(y1,y2), fill=fill, stroke="none")
    else:
        rect(min(x1,x2), y1 - t/2, max(x1,x2), y1 + t/2, fill=fill, stroke="none")

def shear(x1, y1, x2, y2, t=W_SHEAR):
    wall(x1, y1, x2, y2, t, fill="#000")

def glass(x1, y1, x2, y2):
    line(x1, y1, x2, y2, stroke="#1f6fb2", sw=35)
    if x1 == x2:
        line(x1-70, y1, x2-70, y2, stroke="#1f6fb2", sw=15); line(x1+70, y1, x2+70, y2, stroke="#1f6fb2", sw=15)
    else:
        line(x1, y1-70, x2, y2-70, stroke="#1f6fb2", sw=15); line(x1, y1+70, x2, y2+70, stroke="#1f6fb2", sw=15)

def window(x1, y1, x2, y2):
    """Window in an exterior wall: three thin parallel lines."""
    if x1 == x2:
        for d in (-90, 0, 90): line(x1+d, y1, x2+d, y2, stroke="#1f6fb2", sw=18)
    else:
        for d in (-90, 0, 90): line(x1, y1+d, x2, y2+d, stroke="#1f6fb2", sw=18)

def door(hx, hy, w, direction, swing):
    """Door leaf hinged at (hx,hy). direction: unit vector of the closed leaf along the wall
    ('E','W','N','S'); swing: 'cw' or 'ccw' (rotation from closed position, screen coords)."""
    dirs = {"E": (1,0), "W": (-1,0), "N": (0,-1), "S": (0,1)}
    dx, dy = dirs[direction]
    ang0 = math.atan2(dy, dx)
    ang1 = ang0 + (math.pi/2 if swing == "cw" else -math.pi/2)
    ex, ey = hx + w*math.cos(ang1), hy + w*math.sin(ang1)   # open leaf end
    cx, cy = hx + w*math.cos(ang0), hy + w*math.sin(ang0)   # closed leaf end
    line(hx, hy, ex, ey, sw=40)
    sweep = 1 if swing == "cw" else 0
    add(f'<path d="M {cx} {cy} A {w} {w} 0 0 {sweep} {ex} {ey}" fill="none" stroke="#000" stroke-width="15" stroke-dasharray="60 40"/>')

def hatch_rect(x1, y1, x2, y2, label=None, size=200):
    rect(x1, y1, x2, y2, fill="url(#hatch)", sw=18)
    if label: text((x1+x2)/2, (y1+y2)/2 + size*0.35, label, size)

def stripes_rect(x1, y1, x2, y2, step=150, horizontal=True):
    rect(x1, y1, x2, y2, sw=18)
    if horizontal:
        y = y1 + step
        while y < y2:
            line(x1, y, x2, y, sw=10); y += step
    else:
        x = x1 + step
        while x < x2:
            line(x, y1, x, y2, sw=10); x += step

def label(x, y, name, dim=None, size=330):
    text(x, y, name, size, weight="bold")
    if dim: text(x, y + size*1.1, dim, size*0.7, fill="#444")

def dim_chain_h(y, xs, segs, above=True, total=None, size=260):
    """Horizontal dimension chain starting at x=xs with segment lengths segs."""
    x = xs
    line(xs, y, xs + sum(segs), y, sw=18)
    pts = [xs]
    for s in segs:
        x += s; pts.append(x)
    for p in pts:
        line(p, y-120, p, y+120, sw=18)
        line(p-80, y+80, p+80, y-80, sw=25)
    for i, s in enumerate(segs):
        cx = (pts[i] + pts[i+1]) / 2
        text(cx, y - 70 if above else y + size + 50, str(s), size)
    if total is not None:
        yt = y - 900 if above else y + 900
        line(xs, yt, xs + sum(segs), yt, sw=18)
        for p in (xs, xs + sum(segs)):
            line(p, yt-120, p, yt+120, sw=18); line(p-80, yt+80, p+80, yt-80, sw=25)
        text(xs + sum(segs)/2, yt - 70 if above else yt + size + 50, str(total), size)

def dim_chain_v(x, ys, segs, left=True, total=None, size=260):
    y = ys
    line(x, ys, x, ys + sum(segs), sw=18)
    pts = [ys]
    for s in segs:
        y += s; pts.append(y)
    for p in pts:
        line(x-120, p, x+120, p, sw=18)
        line(x-80, p+80, x+80, p-80, sw=25)
    for i, s in enumerate(segs):
        cy = (pts[i] + pts[i+1]) / 2
        tx = x - 80 if left else x + 80
        text(tx, cy, str(s), size, rotate=-90, extra='dominant-baseline="auto"' if left else 'dominant-baseline="hanging"')
    if total is not None:
        xt = x - 900 if left else x + 900
        line(xt, ys, xt, ys + sum(segs), sw=18)
        for p in (ys, ys + sum(segs)):
            line(xt-120, p, xt+120, p, sw=18); line(xt-80, p+80, xt+80, p-80, sw=25)
        text(xt - 80 if left else xt + 80, ys + sum(segs)/2, str(total), size, rotate=-90,
             extra='dominant-baseline="auto"' if left else 'dominant-baseline="hanging"')

# ---------- canvas ----------
X0, Y0, X1, Y1 = -3600, -4700, 21400, 22600
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0} {Y0} {X1-X0} {Y1-Y0}" width="{(X1-X0)/10}" height="{(Y1-Y0)/10}">')
add('<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="160" height="160" patternTransform="rotate(45)">'
    '<line x1="0" y1="0" x2="0" y2="160" stroke="#555" stroke-width="14"/></pattern>'
    '<pattern id="core" patternUnits="userSpaceOnUse" width="220" height="220" patternTransform="rotate(45)">'
    '<line x1="0" y1="0" x2="0" y2="220" stroke="#9a9a9a" stroke-width="18"/></pattern></defs>')
rect(X0, Y0, X1, Y1, fill="#ffffff", stroke="none")

# ---------- axis grid (light) ----------
XA = [0, 1300, 4200, 6100, 7800, 10800, 12900, 15850, 18550]
YA = [0, 2400, 3700, 5700, 7600, 10250, 11500, 12900, 15200, 17350]
for x in XA: line(x, -400, x, 17750, stroke="#c9c9c9", sw=12, extra='stroke-dasharray="300 150 40 150"')
for y in YA: line(-400, y, 18950, y, stroke="#c9c9c9", sw=12, extra='stroke-dasharray="300 150 40 150"')

# ---------- public core (hatched) ----------
rect(12900, 5700, 18550, 7600, fill="url(#core)", stroke="none")     # 走道
rect(12900, 7600, 15850, 17350, fill="url(#core)", stroke="none")    # 电梯厅/楼梯
for (a, b) in ((7600, 10250), (10250, 12900), (12900, 15200)):       # 电梯
    rect(15850, a, 18550, b, fill="#f2f2f2", stroke="none")
    rect(16150, a+300, 18250, b-300, sw=18)
    line(16150, a+300, 18250, b-300, sw=12); line(16150, b-300, 18250, a+300, sw=12)
    text(17200, (a+b)/2 + 100, "电梯", 280)
rect(15850, 15200, 18550, 17350, fill="#f2f2f2", stroke="none"); text(17200, 16350, "设备/管井", 260)
# stairs
sx1, sx2 = 13300, 14600
rect(sx1, 11200, sx2, 16600, fill="#fff", sw=18)
yy = 11200
while yy <= 16600:
    line(sx1, yy, sx2, yy, sw=12); yy += 270
line((sx1+sx2)/2, 16500, (sx1+sx2)/2, 11400, sw=30, extra='marker-end="url(#arrow)"')
add('<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#000"/></marker></defs>')
text(13950, 10700, "楼梯", 300)
text(14400, 9000, "电梯厅", 320)
text(15700, 6750, "公共走道", 320)

# ---------- exterior envelope ----------
wall(0, 0, 10800, 0, W_EXT)
wall(0, 0, 0, 3700, W_EXT); wall(0, 11500, 0, 15200, W_EXT)
wall(0, 15200, 10800, 15200, W_EXT)
wall(10800, 0, 10800, 700, W_EXT)
wall(12900, 700, 12900, 5700, W_EXT)
shear(12900, 5700, 12900, 6000); shear(12900, 7300, 12900, 17350)   # core shear wall / entrance
wall(12900, 5700, 18550, 5700, W_EXT); wall(12900, 7600, 18550, 7600, W_EXT)
wall(18550, 5700, 18550, 17350, W_EXT); wall(12900, 17350, 18550, 17350, W_EXT)
wall(15850, 7600, 15850, 17350, W_INT)
for y in (10250, 12900, 15200): wall(15850, y, 18550, y, W_INT)
# AC ledges & balcony railings (thin)
rect(10800, 700, 12900, 1300, sw=25); rect(11300, 800, 12500, 1200, sw=18); text(11900, 1080, "空调机位", 220)
line(10800, 1300, 12900, 1300, sw=35)
rect(10800, 14400, 12900, 15200, sw=25); rect(11300, 14550, 12500, 15050, sw=18); text(11900, 14880, "空调机位", 220)
line(10800, 14400, 12900, 14400, sw=35)
# west balcony railing (glass balustrade)
window(0, 3700, 0, 11500)

# ---------- interior walls ----------
# row 1
shear(0, 3700, 5700, 3700)                       # 主卧/多功能室 (剪力墙)
wall(6900, 3700, 10800, 3700)
wall(4200, 0, 4200, 2600); wall(4200, 3500, 4200, 3700)
wall(4200, 2400, 6400, 2400); wall(7200, 2400, 7800, 2400)
wall(7800, 0, 7800, 2700); wall(7800, 3500, 7800, 3700)
wall(10800, 0, 10800, 4100); wall(10800, 4900, 10800, 5700)
wall(11700, 2400, 12900, 2400); wall(10800, 2400, 10900, 2400)
wall(10800, 5700, 12900, 5700)
wall(10050, 5700, 10800, 5700)
# kitchen/entry
wall(10200, 5700, 10200, 6000); wall(10200, 7300, 10200, 10250)
wall(12000, 7600, 12900, 7600); wall(12000, 7600, 12000, 9500); wall(12000, 9500, 12900, 9500)
wall(9700, 10250, 12900, 10250)
wall(9700, 10250, 9700, 10350); wall(9700, 11300, 9700, 11500)
glass(9700, 10350, 9700, 11300)
# row 2
shear(1300, 3700, 1300, 4300); shear(1300, 7300, 1300, 8500); shear(1300, 10300, 1300, 11500)
glass(1300, 4300, 1300, 7300); glass(1300, 8500, 1300, 10300)
wall(1300, 7600, 5500, 7600, 300)
shear(5500, 6900, 5500, 7900, 300)               # 保留剪力墙段（推测）
glass(5600, 3700, 5600, 6900)
# row 3/4
shear(0, 11500, 5700, 11500)
wall(7000, 11500, 10800, 11500)
wall(10800, 11500, 10800, 15200)
wall(10800, 12900, 10900, 12900); wall(11700, 12900, 12900, 12900)
wall(4200, 11500, 4200, 11700); wall(4200, 12500, 4200, 15200)
wall(7800, 11500, 7800, 11700); wall(7800, 12500, 7800, 15200)
wall(4200, 12400, 4500, 12400); wall(5300, 12400, 6500, 12400); wall(7300, 12400, 7800, 12400)
wall(6100, 12400, 6100, 15200)

# ---------- windows ----------
window(300, 0, 4000, 0)            # 主卧北
window(0, 2000, 0, 3000)           # 主卧西飘窗
window(8000, 0, 10600, 0)          # 衣帽间北
window(300, 15200, 3900, 15200)    # 卧室南
window(4400, 15200, 5900, 15200); window(6300, 15200, 7700, 15200)
window(8000, 15200, 10600, 15200)  # 儿童房南
window(0, 11700, 0, 14900)         # 卧室西
window(10900, 1300, 12800, 1300)   # 阳台(北)

# ---------- doors ----------
door(4200, 3500, 900, "N", "ccw")          # 过厅→主卧
door(7200, 2400, 800, "W", "ccw")          # 过厅→主卫
door(5700, 3700, 600, "E", "ccw"); door(6900, 3700, 600, "W", "cw")   # 双开门
door(10800, 4900, 800, "N", "cw")          # 西厨→家政
door(10900, 2400, 800, "E", "ccw")         # 家政→阳台
door(10050, 5700, 850, "W", "ccw")         # 餐厅→西厨侧门
door(12900, 6100, 1100, "S", "cw")         # 入户门
door(4200, 11700, 800, "S", "cw")          # 卧室
door(7800, 11700, 800, "S", "ccw")         # 儿童卧室
door(4500, 12400, 800, "E", "cw")          # 客卫A
door(7300, 12400, 800, "W", "ccw")         # 客卫B
door(10900, 12900, 800, "E", "cw")         # 中厨→阳台

# ---------- furniture ----------
# 主卧室
rect(300, 300, 4000, 850, sw=18); rect(1300, 300, 3400, 850, fill="#eee", sw=18)
circle(800, 575, 120); circle(3650, 575, 120)
rect(1300, 850, 3400, 3000, sw=25); line(1300, 1400, 3400, 1400, sw=15)
rect(1400, 950, 2300, 1350, sw=12); rect(2400, 950, 3300, 1350, sw=12)
# 主卫
rect(5900, 200, 7100, 1300, fill="#eef5fb", sw=18); line(5900, 1300, 7100, 1300, stroke="#1f6fb2", sw=30); circle(6500, 500, 90)
add('<ellipse cx="4950" cy="750" rx="230" ry="330" fill="none" stroke="#000" stroke-width="18"/>'); rect(4700, 300, 5200, 520, sw=15)
rect(4600, 1500, 6300, 2300, sw=18, extra='rx="300"'); rect(4750, 1620, 6150, 2180, sw=12, extra='rx="250"')
rect(7000, 900, 7750, 2300, sw=18); add('<ellipse cx="7375" cy="1250" rx="230" ry="200" fill="none" stroke="#000" stroke-width="15"/>')
add('<ellipse cx="7375" cy="1950" rx="230" ry="200" fill="none" stroke="#000" stroke-width="15"/>')
hatch_rect(4300, 300, 4600, 1500)
# 衣帽间
stripes_rect(8000, 300, 8600, 3500); stripes_rect(10000, 300, 10600, 3500)
rect(8900, 1200, 9700, 3300, sw=18)
# 家政
hatch_rect(12200, 2600, 12700, 5500)
rect(10950, 2550, 11550, 3150, sw=18); circle(11250, 2850, 220)
# 多功能室
hatch_rect(1700, 3900, 5500, 4300)
circle(2500, 4800, 320); circle(2500, 4800, 120)
rect(2900, 4400, 3700, 5100, sw=15, extra='rx="150"')
rect(3700, 6400, 4600, 6900, sw=18); hatch_rect(2400, 6950, 5300, 7300)
# 西厨
hatch_rect(7000, 3900, 10600, 4300)
rect(7000, 4900, 9400, 5700, sw=22); circle(9000, 5300, 200); rect(7200, 5050, 8300, 5550, sw=12)
circle(7600, 6000, 220); circle(8300, 6000, 220)
hatch_rect(9500, 5000, 10700, 5600)
# 餐厅
rect(7200, 8700, 8600, 10100, sw=22)
for yy in (8850, 9350, 9850):
    rect(6750, yy, 7150, yy+350, sw=12); rect(8650, yy, 9050, yy+350, sw=12)
hatch_rect(7100, 11000, 9500, 11400)
hatch_rect(9600, 8100, 10100, 9400)
circle(9800, 7750, 250)
# 客厅
line(3200, 7800, 4600, 7800, sw=60)
rect(1900, 8900, 2600, 11100, sw=18); rect(2600, 10400, 5600, 11100, sw=18)
for xx in range(2650, 5500, 700): line(xx, 10400, xx, 11100, sw=10)
circle(3850, 9450, 420); circle(3850, 9450, 300)
rect(2800, 8400, 5600, 10300, sw=10, extra='stroke-dasharray="80 80"')
# 玄关/储物
hatch_rect(11400, 7700, 11900, 9500); hatch_rect(10400, 9650, 11900, 10200)
hatch_rect(12100, 7700, 12750, 9400, "SP", 240)
# 中厨
hatch_rect(12100, 10400, 12700, 12750)
circle(12400, 11000, 180); circle(12400, 11700, 150); circle(12400, 12050, 150)
# 卧室
rect(300, 14400, 3450, 14900, sw=18); rect(1100, 14400, 2900, 14900, fill="#eee", sw=18)
circle(700, 14650, 120); circle(3150, 14650, 120)
rect(1100, 12400, 2900, 14400, sw=25); line(1100, 13850, 2900, 13850, sw=15)
rect(1200, 13950, 1950, 14300, sw=12); rect(2050, 13950, 2800, 14300, sw=12)
stripes_rect(3500, 12400, 4100, 14900)
# 客卫 A / B
for ox, sgn in ((0, 1), (0, -1)):
    pass
add('<ellipse cx="5700" cy="12850" rx="200" ry="280" fill="none" stroke="#000" stroke-width="15"/>'); rect(5500, 12500, 5900, 12700, sw=12)
add('<ellipse cx="6500" cy="12850" rx="200" ry="280" fill="none" stroke="#000" stroke-width="15"/>'); rect(6300, 12500, 6700, 12700, sw=12)
rect(4500, 13300, 5900, 13800, sw=15); add('<ellipse cx="5200" cy="13550" rx="260" ry="170" fill="none" stroke="#000" stroke-width="12"/>')
rect(6300, 13300, 7700, 13800, sw=15); add('<ellipse cx="7000" cy="13550" rx="260" ry="170" fill="none" stroke="#000" stroke-width="12"/>')
rect(4500, 13950, 5900, 14950, fill="#eef5fb", sw=15); circle(5200, 14450, 90); line(4500, 13950, 5900, 13950, stroke="#1f6fb2", sw=30)
rect(6300, 13950, 7700, 14950, fill="#eef5fb", sw=15); circle(7000, 14450, 90); line(6300, 13950, 7700, 13950, stroke="#1f6fb2", sw=30)
# 儿童卧室
hatch_rect(8700, 11600, 10600, 12100)
rect(8200, 12900, 9800, 14900, sw=25); line(9300, 12900, 9300, 14900, sw=15)
rect(9400, 13000, 9700, 13800, sw=12); rect(9400, 14000, 9700, 14800, sw=12)
rect(9800, 12900, 10400, 14900, fill="#eee", sw=18); circle(10100, 13200, 120)
# 阳台(南) 洗衣
rect(11900, 13000, 12500, 13600, sw=15); circle(12200, 13300, 200)

# ---------- room labels (轴线尺寸为推算) ----------
label(2100, 2000, "主卧室", "约4.2×3.7")
label(5450, 1400, "主卫生间", "约3.6×2.4", 280)
label(6000, 3100, "过厅", None, 260)
label(9300, 700, "衣帽间", "约3.0×3.7", 300)
label(11850, 1950, "阳台", "约2.1×1.1", 260)
label(11800, 3900, "家政多功能室", "约2.1×3.3", 260)
label(650, 7700, "休闲阳台", None, 260)
text(650, 8300, "约1.3×7.8", 200, fill="#444")
label(3400, 5700, "多功能室", "约4.3×3.9")
label(8200, 4650, "西厨", "约5.2×2.0", 300)
label(7900, 8300, "餐厅", None, 330)
label(3700, 8500, "客厅", "约4.3×3.9")
label(11550, 6700, "玄关", None, 300)
label(11100, 8800, "储物/收纳", None, 240)
label(11000, 10900, "中厨", None, 300)
label(2100, 13300, "卧室", "约4.2×3.7")
label(5150, 14100, "客卫生间", "约1.9×2.8", 230)
label(7000, 14100, "客卫生间", "约1.7×2.8", 230)
label(9000, 12600, "儿童卧室", "约3.0×3.7", 300)
label(11850, 13900, "阳台", "约2.1×1.5", 260)
text(6000, 12050, "走道", 240)

# ---------- dimension chains (原图标注) ----------
XS = [1300, 2900, 1900, 1700, 3000, 2100, 2950, 2700]
YS = [2400, 1300, 2000, 1900, 2650, 1250, 1400, 2300, 2150]
dim_chain_h(-1100, 0, XS, above=True, total=18550)
dim_chain_h(18450, 0, XS, above=False, total=18550)
dim_chain_v(-1100, 0, YS, left=True, total=17350)
dim_chain_v(19650, 0, YS, left=False, total=17350)
# axis bubbles
cum = 0
for i, x in enumerate(XA):
    circle(x, -2650, 230, fill="#fff"); text(x, -2560, str(i+1), 260)
for i, y in enumerate(YA):
    circle(-2650, y, 230, fill="#fff"); text(-2650, y+90, chr(ord("A")+i), 260)

# ---------- north arrow, title, legend ----------
nx, ny = 20200, 1200
add(f'<path d="M {nx} {ny-700} L {nx+250} {ny+300} L {nx} {ny+100} L {nx-250} {ny+300} Z" fill="#000"/>')
text(nx, ny+750, "北", 320, weight="bold")
text(X0+300, Y0+700, "深业世纪山谷 3C栋 04+05打通户型  建面约262㎡  平面图（高清重绘版）", 520, anchor="start", weight="bold")
text(X0+300, Y0+1350, "外围尺寸链（mm）为开发商原图标注；室内隔墙、门窗、家具位置按原图比例推算，误差约±200mm。室内“约a×b”为轴线尺寸估算（m）。本图非施工图、非测绘成果。", 260, anchor="start", fill="#333")
# legend
lx, ly = 12900, 19900
rect(lx, ly, lx+600, ly+250, fill="#000", stroke="none"); text(lx+750, ly+220, "剪力墙/核心筒墙（按原图线宽推测）", 240, anchor="start")
rect(lx, ly+450, lx+600, ly+650, fill="#2b2b2b", stroke="none"); text(lx+750, ly+630, "隔墙", 240, anchor="start")
line(lx, ly+1000, lx+600, ly+1000, stroke="#1f6fb2", sw=35); text(lx+750, ly+1080, "玻璃隔断 / 窗 / 栏板", 240, anchor="start")
rect(lx, ly+1300, lx+600, ly+1550, fill="url(#hatch)", sw=15); text(lx+750, ly+1500, "固定柜体", 240, anchor="start")
rect(lx, ly+1750, lx+600, ly+2000, fill="url(#core)", stroke="none"); text(lx+750, ly+1950, "公共区域（走道/电梯厅/楼梯）", 240, anchor="start")
# scale bar
sbx, sby = 0, 20400
for i in range(5):
    rect(sbx+i*1000, sby, sbx+(i+1)*1000, sby+180, fill="#000" if i % 2 == 0 else "#fff", sw=15)
for i in range(0, 6): text(sbx+i*1000, sby+500, f"{i}m", 230)
text(X0+300, 22250, "原图来源：开发商宣传户型图（用户提供）。重绘：2026-11。", 230, anchor="start", fill="#555")

add('</svg>')
svg = "\n".join(out)
open("/tmp/plan262/3C_262_0405打通_高清重绘_带尺寸.svg", "w", encoding="utf-8").write(svg)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to="/tmp/plan262/3C_262_0405打通_高清重绘_带尺寸.png", output_width=6000)
cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to="/tmp/plan262/3C_262_0405打通_高清重绘_带尺寸.pdf")
print("done")
