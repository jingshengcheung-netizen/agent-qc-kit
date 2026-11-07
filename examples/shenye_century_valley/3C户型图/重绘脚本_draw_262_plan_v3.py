# -*- coding: utf-8 -*-
"""深业世纪山谷 3C栋 04+05 打通户型（建面约262㎡）高清重绘 v3
单位 mm。外围尺寸链取自开发商原图标注；墙体/玻璃/门窗位置按原图像素比例推算
（标定 x: 0.0390 px/mm, y: 0.0385 px/mm；误差约 ±200 mm）。
输出：SVG / PNG / PDF。运行：python3 make_plan_v2.py [输出目录]
"""
import math, sys, os, json
import cairosvg

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
FONT = "WenQuanYi Micro Hei, Noto Sans CJK SC, Droid Sans Fallback, sans-serif"

C_SOLID, C_SHEAR, C_LIGHT, C_GLASS = "#3a3a3a", "#000000", "#6a6a6a", "#1769aa"
C_DIM_WALL, C_DIM_GLASS, C_DIM_DOOR, C_AXIS = "#444444", "#1769aa", "#b3261e", "#111111"

out = []
def add(s): out.append(s)

# ------------------------------------------------------------------ primitives
def rect(x1, y1, x2, y2, fill="none", stroke="#000", sw=18, extra=""):
    add(f'<rect x="{min(x1,x2):.0f}" y="{min(y1,y2):.0f}" width="{abs(x2-x1):.0f}" height="{abs(y2-y1):.0f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def line(x1, y1, x2, y2, stroke="#000", sw=18, extra=""):
    add(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

def circle(cx, cy, r, fill="none", stroke="#000", sw=18):
    add(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def ellipse(cx, cy, rx, ry, sw=15):
    add(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="#000" stroke-width="{sw}"/>')

def text(x, y, s, size=300, anchor="middle", fill="#000", weight="normal", rotate=0, baseline=None):
    tr = f' transform="rotate({rotate} {x:.0f} {y:.0f})"' if rotate else ""
    db = f' dominant-baseline="{baseline}"' if baseline else ""
    add(f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}" '
        f'fill="{fill}" font-weight="{weight}"{tr}{db}>{s}</text>')

# ------------------------------------------------------------------ building elements
def solid(x1, y1, x2, y2):            # 实墙（原图白色填充）
    rect(x1, y1, x2, y2, fill=C_SOLID, stroke="none")

def shear(x1, y1, x2, y2):            # 原图点状填充的柱/墙垛（疑似结构构件）
    rect(x1, y1, x2, y2, fill="url(#col)", stroke="#000", sw=20)

def hollowbox(x1, y1, x2, y2):        # 原图空心矩形（柱/矮墙）
    rect(x1, y1, x2, y2, fill="#e9e9e9", stroke="#000", sw=26)

def tv(x1, x2, y, up):                # 电视（原图：细长矩形 + 视角线）
    rect(x1, y - (60 if up else 0), x2, y + (0 if up else 60), fill="#000", stroke="none")
    cx = (x1 + x2) / 2; d = -1 if up else 1
    for dx in (-450, 0, 450): line(cx, y, cx + dx, y + d*520, sw=10, extra='stroke-dasharray="40 40"')

def slide(x1, y1, x2, y2, leaf_from, leaf_to):   # 推拉门：门洞细线 + 门扇粗条
    line(x1, y1, x2, y2, stroke="#000", sw=12)
    if x1 == x2:
        rect(x1-45, leaf_from, x1+45, leaf_to, fill="#fff", stroke="#000", sw=22)
    else:
        rect(leaf_from, y1-45, leaf_to, y1+45, fill="#fff", stroke="#000", sw=22)

def light(x1, y1, x2, y2):            # 轻质隔断（原图空心双线）
    rect(x1, y1, x2, y2, fill="#ffffff", stroke=C_LIGHT, sw=28)

def glass(x1, y1, x2, y2):            # 外窗 / 玻璃
    line(x1, y1, x2, y2, stroke=C_GLASS, sw=40)
    if x1 == x2:
        line(x1-75, y1, x2-75, y2, stroke=C_GLASS, sw=14); line(x1+75, y1, x2+75, y2, stroke=C_GLASS, sw=14)
    else:
        line(x1, y1-75, x2, y2-75, stroke=C_GLASS, sw=14); line(x1, y1+75, x2, y2+75, stroke=C_GLASS, sw=14)

def rail(x1, y1, x2, y2):             # 玻璃栏板（原图双线）
    if x1 == x2:
        line(x1-60, y1, x2-60, y2, stroke=C_GLASS, sw=22); line(x1+60, y1, x2+60, y2, stroke=C_GLASS, sw=22)
    else:
        line(x1, y1-60, x2, y2-60, stroke=C_GLASS, sw=22); line(x1, y1+60, x2, y2+60, stroke=C_GLASS, sw=22)

def hatch(x1, y1, x2, y2, label=None, size=170):   # 固定柜体
    rect(x1, y1, x2, y2, fill="url(#cab)", sw=15)
    if label: text((x1+x2)/2, (y1+y2)/2 + size*0.35, label, size)

def stripes(x1, y1, x2, y2, step=140):             # 挂衣柜
    rect(x1, y1, x2, y2, sw=15)
    if abs(x2-x1) < abs(y2-y1):
        y = min(y1,y2) + step
        while y < max(y1,y2): line(x1, y, x2, y, sw=8); y += step
    else:
        x = min(x1,x2) + step
        while x < max(x1,x2): line(x, y1, x, y2, sw=8); x += step

def door(hx, hy, w, closed_dir, swing, label=True):
    """单扇平开门。hx,hy=铰链点；closed_dir=关闭时门扇方向(E/W/N/S)；swing=cw/ccw。"""
    dirs = {"E": (1,0), "W": (-1,0), "N": (0,-1), "S": (0,1)}
    dx, dy = dirs[closed_dir]
    a0 = math.atan2(dy, dx); a1 = a0 + (math.pi/2 if swing == "cw" else -math.pi/2)
    cx, cy = hx + w*math.cos(a0), hy + w*math.sin(a0)
    ex, ey = hx + w*math.cos(a1), hy + w*math.sin(a1)
    line(hx, hy, ex, ey, sw=38)
    add(f'<path d="M {cx:.0f} {cy:.0f} A {w} {w} 0 0 {1 if swing=="cw" else 0} {ex:.0f} {ey:.0f}" '
        f'fill="none" stroke="#000" stroke-width="14" stroke-dasharray="70 45"/>')

def dim(x1, y1, x2, y2, side=1, off=150, prefix="", color=C_DIM_WALL, size=150, value=None):
    """在线段旁标注长度。side=+1 表示文字放在线段的 +法向一侧（横线→下方，竖线→右侧）。"""
    L = value if value is not None else math.hypot(x2-x1, y2-y1)
    s = f"{prefix}{int(round(L/10.0)*10)}"
    mx, my = (x1+x2)/2, (y1+y2)/2
    tw = size*0.56*sum(2 if ord(ch) > 255 else 1 for ch in s) + 60
    if abs(y2-y1) < 1:   # horizontal
        ty = my + side*off + (size*0.75 if side > 0 else 0)
        rect(mx-tw/2, ty-size*0.78, mx+tw/2, ty+size*0.22, fill="#ffffff", stroke="none")
        text(mx, ty, s, size, fill=color)
    else:                # vertical
        tx = mx + side*off + (size*0.75 if side > 0 else 0)
        rect(tx-size*0.78, my-tw/2, tx+size*0.22, my+tw/2, fill="#ffffff", stroke="none")
        text(tx, my, s, size, fill=color, rotate=-90)

def gdim(x1, y1, x2, y2, side=1, off=150, prefix="窗", value=None):
    dim(x1, y1, x2, y2, side, off, prefix, C_DIM_GLASS, 150, value)

def ddim(x1, y1, x2, y2, side=1, off=150, prefix="门", value=None):
    dim(x1, y1, x2, y2, side, off, prefix, C_DIM_DOOR, 150, value)

def poly_area(p):
    a = 0
    for i in range(len(p)):
        x1, y1 = p[i]; x2, y2 = p[(i+1) % len(p)]
        a += x1*y2 - x2*y1
    return abs(a) / 2 / 1e6

ROOMS = []
def room(name, poly, lx, ly, size=320, note=None, count=True):
    """房间名 + 面积（写在名下）。poly 为净空多边形（墙面围合）。"""
    A = poly_area(poly)
    ROOMS.append((name, A, count))
    text(lx, ly, name, size, weight="bold")
    text(lx, ly + size*0.95, f"约{A:.1f}㎡", size*0.72, fill="#222")
    if note: text(lx, ly + size*1.65, note, size*0.5, fill="#666")
    add(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x,y in poly)}" fill="none" stroke="#9aa" stroke-width="8" stroke-dasharray="40 60"/>')

# ------------------------------------------------------------------ canvas
X0, Y0, X1, Y1 = -3900, -5000, 21500, 23200
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0} {Y0} {X1-X0} {Y1-Y0}" width="{(X1-X0)/10}" height="{(Y1-Y0)/10}">')
add('<defs>'
    '<pattern id="cab" patternUnits="userSpaceOnUse" width="150" height="150" patternTransform="rotate(45)">'
    '<line x1="0" y1="0" x2="0" y2="150" stroke="#555" stroke-width="12"/></pattern>'
    '<pattern id="core" patternUnits="userSpaceOnUse" width="240" height="240" patternTransform="rotate(45)">'
    '<line x1="0" y1="0" x2="0" y2="240" stroke="#a8a8a8" stroke-width="16"/></pattern>'
    '<pattern id="col" patternUnits="userSpaceOnUse" width="90" height="90"><rect width="90" height="90" fill="#777"/><circle cx="45" cy="45" r="22" fill="#fff"/></pattern><pattern id="ac" patternUnits="userSpaceOnUse" width="120" height="120">'
    '<line x1="0" y1="0" x2="120" y2="0" stroke="#888" stroke-width="10"/></pattern>'
    '<marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#000"/></marker>'
    '</defs>')
rect(X0, Y0, X1, Y1, fill="#ffffff", stroke="none")

# 轴网（浅）
XA = [0, 1300, 4200, 6100, 7800, 10800, 12900, 15850, 18550]
YA = [0, 2400, 3700, 5700, 7600, 10250, 11500, 12900, 15200, 17350]
for x in XA: line(x, -500, x, 17850, stroke="#d5d5d5", sw=10, extra='stroke-dasharray="300 150 40 150"')
for y in YA: line(-700, y, 19050, y, stroke="#d5d5d5", sw=10, extra='stroke-dasharray="300 150 40 150"')

# ================================================================== 公共区域（核心筒）
rect(12900, 7440, 18550, 17350, fill="url(#core)", stroke="none")
solid(12456, 5500, 13841, 5830); rail(13841, 5665, 18550, 5665)            # 走道北墙（原图 13841 以东为双线）
solid(18300, 5500, 18550, 17350); solid(12456, 17100, 16020, 17350)
for a, b in ((7500, 10250), (10250, 12900), (12900, 15490)):
    solid(15660, a, 16020, b); solid(16020, a-120, 18300, a+120)
    rect(16250, a+350, 18100, b-350, fill="#f4f4f4", sw=16)
    line(16250, a+350, 18100, b-350, sw=10); line(16250, b-350, 18100, a+350, sw=10)
    text(17175, (a+b)/2 + 90, "电梯", 260)
    dm = (a+b)/2; rect(15660, dm-500, 16020, dm+500, fill="#ffffff", stroke="none")   # 电梯门洞
solid(16020, 15490-120, 18300, 15490+120)
text(17175, 16450, "设备/管井", 240)
sx1, sx2 = 13300, 14600
rect(sx1, 11200, sx2, 16600, fill="#fff", sw=16)
yy = 11200
while yy <= 16600: line(sx1, yy, sx2, yy, sw=10); yy += 270
line((sx1+sx2)/2, 16450, (sx1+sx2)/2, 11450, sw=28, extra='marker-end="url(#arrow)"')
text(13950, 10800, "楼梯", 280); text(14300, 9000, "电梯厅", 300)
text(15700, 6700, "公共走道", 300, fill="#333")

# ================================================================== 外围护
# --- 北 y=0（外皮在轴线，实墙向内 250）
glass(0, 0, 1000, 0);          gdim(0, 0, 1000, 0, side=1, off=330)
line(230, 230, 1010, 230, sw=10)                       # 窗台线（原图）
solid(1000, 0, 4500, 250);     dim(1000, 0, 4500, 0, side=1, off=330)
glass(4500, 0, 7880, 0);       gdim(4500, 0, 7880, 0, side=1, off=330)
glass(7880, 0, 9450, 0);       gdim(7880, 0, 9450, 0, side=1, off=330)
line(8750, 150, 9450, 150, sw=10)
solid(9450, 0, 10875, 250);    dim(9450, 0, 10875, 0, side=1, off=330)
# --- 西 x=0
glass(0, 0, 0, 2900);          gdim(0, 0, 0, 2900, side=1, off=330)
solid(0, 2900, 250, 3650);     dim(0, 2900, 0, 3650, side=1, off=330)
solid(-300, 3650, 1250, 4100)                          # 休闲阳台北端墙（约450厚）
rail(-300, 4100, -300, 11150); gdim(-300, 4100, -300, 11150, side=1, off=200, prefix="玻璃栏板")
line(-150, 4100, -150, 11150, sw=8)
solid(-300, 11150, 1700, 11650)                        # 休闲阳台南端墙（约500厚）
solid(0, 11650, 250, 12400);   dim(0, 11650, 0, 12400, side=1, off=330)
glass(0, 12400, 0, 15200);     gdim(0, 12400, 0, 15200, side=1, off=330)
# --- 南 y=15200（外皮在轴线，实墙向内 250）
glass(0, 15200, 1000, 15200);  gdim(0, 15200, 1000, 15200, side=-1, off=330)
line(350, 15000, 1020, 15000, sw=10)
solid(1000, 14950, 4500, 15200); dim(1000, 15200, 4500, 15200, side=-1, off=330)
glass(4500, 15200, 6075, 15200); gdim(4500, 15200, 6075, 15200, side=-1, off=330)
glass(6225, 15200, 7735, 15200); gdim(6225, 15200, 7735, 15200, side=-1, off=330)
glass(7885, 15200, 9450, 15200); gdim(7885, 15200, 9450, 15200, side=-1, off=330)
solid(9450, 14950, 10875, 15200); dim(9450, 15200, 10875, 15200, side=-1, off=330)
# --- 东侧 x=10800 实墙（10625–10875）
solid(10625, 0, 10875, 4075)
dim(10875, 0, 10875, 1300, side=1, off=120)            # 对空调机位段
dim(10875, 1300, 10875, 2400, side=1, off=120)         # 对北阳台段
dim(10625, 2530, 10625, 4075, side=-1, off=120)        # 衣帽间/西厨侧
door(10850, 4850, 775, "N", "cw"); ddim(10850, 4075, 10850, 4850, side=1, off=250)
light(10800, 4850, 10955, 5700); dim(10955, 4850, 10955, 5610, side=1, off=120)
# --- 北阳台 / 空调机位
rect(10875, 700, 12900, 1300, fill="url(#ac)", sw=20); text(11890, 1040, "空调机位", 170, fill="#333")
glass(10875, 1300, 12900, 1300); gdim(10875, 1300, 12900, 1300, side=1, off=120)
glass(12900, 1300, 12900, 2400); gdim(12900, 1300, 12900, 2400, side=-1, off=120)
door(10955, 2425, 760, "E", "ccw"); ddim(10955, 2425, 11715, 2425, side=-1, off=120)
light(11715, 2322, 12650, 2530); dim(11715, 2530, 12650, 2530, side=1, off=120)
# --- 家政室东墙 x=12900（12650–12900）与入口
solid(12650, 2322, 12900, 5830); dim(12650, 2530, 12650, 5610, side=-1, off=120)
light(9500, 5610, 12650, 5830); dim(9890, 5610, 12650, 5610, side=-1, off=120)   # 玄关北墙（空心双线）
solid(9230, 5610, 9500, 6080)                                                     # 墙端柱
ddim(12900, 5830, 12900, 7390, side=1, off=250, prefix="入户门位置·洞口")
line(12650, 5830, 12900, 5830, sw=10); line(12650, 7390, 12900, 7390, sw=10)
solid(12600, 7390, 12900, 12200); dim(12600, 7440, 12600, 12200, side=-1, off=120)
solid(12712, 12200, 12900, 14010); dim(12712, 12200, 12712, 14010, side=-1, off=120)
solid(12507, 14010, 12917, 17350)

# ================================================================== 室内墙体
# --- 剪力墙/结构柱（推测，按原图线宽与位置）
solid(1250, 3650, 1700, 4815);  dim(1700, 3860, 1700, 4815, side=1, off=120)
solid(1250, 6841, 1700, 8425);  dim(1700, 6841, 1700, 7490, side=1, off=120); dim(1700, 7750, 1700, 8425, side=1, off=120)
solid(1250, 10451, 1700, 11650); dim(1700, 10451, 1700, 11350, side=1, off=120)
glass(1450, 4815, 1450, 6841);  gdim(1450, 4815, 1450, 6841, side=1, off=160, prefix="玻璃推拉门")
glass(1450, 8425, 1450, 10451); gdim(1450, 8425, 1450, 10451, side=1, off=160, prefix="玻璃推拉门")
hollowbox(5260, 6910, 5655, 7800); dim(5655, 6910, 5655, 7800, side=1, off=120, prefix="柱/矮墙 400×")   # C2 原图空心矩形
shear(5315, 11230, 5745, 11710)                    # C3 原图点状填充
slide(5510, 11710, 5510, 12633, 11760, 12600); ddim(5510, 11710, 5510, 12633, side=1, off=200, prefix="推拉门")  # 走道内推拉门
shear(9505, 9500, 9890, 9690)                      # K1
shear(9505, 11250, 9890, 11540)                    # K2
solid(10000, 3500, 10875, 4050)                    # 衣帽间东南角实体（原图白色填充）

# --- y≈3700 主卧/多功能室 剪力墙（0–5330），双开门
solid(1700, 3640, 5300, 3860)
dim(1700, 3640, 4070, 3640, side=-1, off=120)          # 主卧侧
dim(4300, 3640, 5300, 3640, side=-1, off=120)          # 过厅侧
tv(1640, 2970, 3640, up=True)                           # 主卧电视（原图此处为电视符号，非门）
line(5300, 3646, 5650, 3646, sw=14); dim(5300, 3646, 5650, 3646, side=-1, off=120, prefix="开口?")   # 原图留空 350
# 过厅双开门：门洞 5745–6890，铰链在 y≈4050（柜体前沿线），向北开入过厅；门套 5650–5745 / 6890–6980
solid(5650, 3370, 5745, 4050); solid(6890, 3370, 6980, 4050)
door(5745, 4050, 575, "E", "ccw"); door(6890, 4050, 575, "W", "cw"); ddim(5745, 4050, 6890, 4050, side=1, off=120, prefix="双开门")
line(5745, 4050, 6890, 4050, sw=12)
# 衣帽间南墙（空心双线）
light(6980, 3620, 10000, 3750); dim(6980, 3620, 10000, 3620, side=-1, off=120)

# --- x≈4200 主卧/主卫
solid(4070, 250, 4300, 1550);  dim(4070, 250, 4070, 1550, side=-1, off=120)
light(4100, 1550, 4240, 2400); dim(4100, 1550, 4100, 2400, side=-1, off=280, prefix="轻质/玻璃?")
ddim(4185, 2550, 4185, 3640, side=-1, off=250, prefix="门洞(原图未画门扇)")
# 主卫南墙 y≈2475（空心双线）+ 门
light(4100, 2400, 6150, 2550);  dim(4300, 2400, 6150, 2400, side=-1, off=120)
door(6150, 2475, 800, "E", "ccw"); ddim(6150, 2475, 6950, 2475, side=-1, off=120)
light(6950, 2400, 7950, 2550);  dim(6950, 2400, 7880, 2400, side=-1, off=120)
# 主卫/衣帽间 x≈7880（空心双线）
light(7815, 0, 7950, 2550);     dim(7950, 100, 7950, 2400, side=1, off=120)
ddim(7880, 2550, 7880, 3620, side=1, off=250, prefix="洞口")

# --- 西厨 / 家政 / 玄关
light(10084, 7415, 10276, 9550); dim(10276, 7440, 10276, 9550, side=1, off=120)
solid(10084, 5830, 10276, 5930)
# 子母门 5930–7415（主扇 1030 北铰链，子扇 420 南铰链，均向西开入餐厅侧）
door(10200, 5930, 1030, "S", "cw"); door(10200, 7415, 420, "N", "ccw")
ddim(10200, 5930, 10200, 7415, side=-1, off=1300, prefix="子母门")
light(9890, 9550, 12712, 9700);  dim(9890, 9700, 12712, 9700, side=1, off=120)
light(11950, 7600, 12600, 9100); text(12275, 8420, "SP", 200); text(12275, 8650, "管井", 160)
# --- 中厨
slide(9700, 9690, 9700, 11250, 9720, 10700); ddim(9700, 9690, 9700, 11250, side=-1, off=160, prefix="推拉门(单扇约980)·洞口")
solid(9890, 11250, 10920, 11600); dim(9890, 11250, 10920, 11250, side=-1, off=120)
solid(10650, 11250, 10920, 15200); dim(10920, 11600, 10920, 12900, side=1, off=120); dim(10650, 11750, 10650, 14950, side=-1, off=120)
door(10920, 12900, 880, "E", "cw"); ddim(10920, 12900, 11800, 12900, side=-1, off=120)
glass(11800, 12900, 12712, 12900); gdim(11800, 12900, 12712, 12900, side=-1, off=120)
# 南阳台 / 空调机位
rail(10920, 14010, 12712, 14010); gdim(10920, 14010, 12712, 14010, side=-1, off=120, prefix="玻璃栏板")
solid(10920, 14130, 11490, 15100)
rect(11490, 14130, 12510, 14790, fill="url(#ac)", sw=20); text(12000, 14500, "空调机位", 170, fill="#333")

# --- y≈7600 客厅/多功能室 墙
solid(1700, 7490, 5335, 7750);  dim(1700, 7750, 5260, 7750, side=1, off=120)
# --- y≈11500 客厅/卧室 墙 + 卧室双开门 1750–2750
solid(1700, 11350, 5315, 11650)
dim(1700, 11650, 4050, 11650, side=1, off=120)
tv(1300, 2690, 11650, up=False)                         # 卧室电视（原图此处为电视符号，非门）
ddim(5745, 11500, 6910, 11500, side=1, off=250, prefix="洞口")
line(5745, 11230, 6910, 11230, sw=10); line(5745, 11680, 6910, 11680, sw=10)
# 餐厅侧矮柜 + 儿童房北侧轻质隔断
hatch(6910, 11250, 9505, 11620)
light(6910, 11646, 9505, 11750); dim(7970, 11750, 9505, 11750, side=1, off=120)
# --- x≈7800 客卫B/儿童房（空心双线）+ 儿童房门
light(7795, 11650, 7970, 11715)
door(7905, 11715, 805, "S", "ccw"); ddim(7905, 11715, 7905, 12520, side=1, off=250)
solid(7795, 12520, 7970, 12633)
light(7795, 12633, 7970, 15200);  dim(7970, 12763, 7970, 14950, side=1, off=120)
# --- 客卫北墙 y≈12700（空心双线）+ 两门
light(4050, 12633, 4650, 12763);  dim(4250, 12633, 4650, 12633, side=-1, off=120)
door(4650, 12700, 780, "E", "ccw"); ddim(4650, 12700, 5430, 12700, side=-1, off=120)
light(5430, 12633, 6910, 12763);  dim(5560, 12633, 6910, 12633, side=-1, off=120)
door(7680, 12700, 770, "W", "ccw"); ddim(6910, 12700, 7680, 12700, side=1, off=120)
light(7680, 12633, 7795, 12763)
# --- 客卫A/B 隔墙 x≈6150
solid(6060, 12633, 6250, 15200);  dim(6250, 12763, 6250, 14950, side=1, off=120)
# --- x≈4200 卧室/客卫A
solid(4050, 12633, 4250, 15200);  dim(4050, 12763, 4050, 14950, side=-1, off=120)
ddim(4150, 11650, 4150, 12633, side=-1, off=250, prefix="门洞(原图未画门扇)")

# ================================================================== 家具（示意）
# 主卧
hatch(250, 250, 4070, 780); rect(1450, 780, 3550, 2850, sw=22); line(1450, 1350, 3550, 1350, sw=12)
rect(1550, 850, 2450, 1250, sw=10); rect(2550, 850, 3450, 1250, sw=10)
# 主卫
hatch(4350, 250, 4950, 1450)
rect(5050, 250, 5600, 850, sw=14); ellipse(5325, 620, 200, 230)
rect(6100, 100, 6600, 850, sw=14); ellipse(6350, 520, 190, 250)
rect(6800, 100, 7800, 860, fill="#eef5fb", sw=14); circle(7300, 480, 80); glass(6800, 860, 7800, 860)
rect(4350, 1540, 6000, 2400, sw=16, extra='rx="300"'); rect(4500, 1660, 5850, 2280, sw=10, extra='rx="250"')
rect(7400, 1050, 7815, 2400, sw=14); ellipse(7607, 1380, 160, 200); ellipse(7607, 2070, 160, 200)
# 衣帽间
stripes(8000, 250, 8550, 2560); stripes(10100, 250, 10600, 3570); rect(8800, 1130, 9770, 3220, sw=16)
# 家政
hatch(12000, 2550, 12550, 5050); rect(10950, 2550, 11550, 3150, sw=14); circle(11250, 2850, 210)
# 多功能室
hatch(1700, 3880, 5520, 4050); hatch(2400, 6950, 5260, 7300)
ellipse(3300, 5600, 1500, 1250); circle(2500, 4800, 300); circle(2500, 4800, 110); rect(2900, 4400, 3700, 5100, sw=12, extra='rx="150"')
# 西厨
hatch(7120, 3760, 9880, 4020); rect(7070, 4050, 9500, 5750, sw=8, extra='stroke-dasharray="60 60"')
rect(7260, 5090, 9390, 5580, sw=20); circle(9100, 5335, 190); rect(7400, 5200, 8500, 5480, sw=10)
circle(7700, 5800, 200); circle(8300, 5800, 200); hatch(9530, 5030, 10625, 5580)
# 餐厅
rect(7550, 8050, 8360, 10300, sw=20)
for yy in (8300, 8950, 9600):
    rect(7150, yy, 7500, yy+450, sw=10); rect(8410, yy, 8760, yy+450, sw=10)
hatch(9530, 8160, 10084, 9440); circle(9800, 7780, 180)
# 玄关/储物
hatch(11400, 7440, 11700, 9100); hatch(10330, 9100, 11700, 9430)
# 中厨
hatch(9890, 9740, 11950, 10260); rect(11970, 9740, 12510, 10230, fill="#555", stroke="none"); text(12240, 10030, "冰箱", 140, fill="#fff")
hatch(12000, 10290, 12600, 12700); circle(12300, 10650, 170); circle(12300, 11400, 140); circle(12300, 11750, 140)
# 客厅
line(2720, 7800, 4100, 7800, sw=55)
rect(1890, 8450, 2680, 10490, sw=16); rect(1890, 10490, 5320, 11200, sw=16)
for xx in range(2680, 5320, 660): line(xx, 10490, xx, 11200, sw=8)
circle(3730, 9580, 400); circle(3730, 9580, 280)
rect(1890, 8450, 5320, 11320, sw=8, extra='stroke-dasharray="60 60"')
# 卧室
rect(1100, 12750, 2930, 14540, sw=22); line(1100, 13950, 2930, 13950, sw=12)
rect(1200, 14050, 1950, 14450, sw=10); rect(2080, 14050, 2830, 14450, sw=10)
hatch(290, 14540, 3500, 15030); stripes(3530, 12620, 4030, 15030)
# 客卫 A / B
rect(4350, 12800, 5990, 13350, sw=12); ellipse(5250, 13075, 220, 150)
rect(6310, 12800, 7735, 13350, sw=12); ellipse(7020, 13075, 220, 150)
rect(4350, 13700, 5050, 14950, fill="#eef5fb", sw=12); circle(4700, 14300, 80); glass(5050, 13700, 5050, 14950)
rect(5400, 14350, 5950, 14950, sw=12); ellipse(5675, 14600, 180, 220)
rect(6300, 13650, 6950, 14950, fill="#eef5fb", sw=12); circle(6625, 14300, 80); glass(6950, 13650, 6950, 14950)
rect(7050, 14350, 7700, 14950, sw=12); ellipse(7375, 14600, 180, 220)
# 儿童卧室
hatch(8700, 11750, 9180, 12200); stripes(9180, 11750, 10640, 12200)
rect(8200, 12900, 9800, 14900, sw=20); line(9300, 12900, 9300, 14900, sw=10)
rect(9400, 13000, 9700, 13850, sw=10); rect(9400, 13950, 9700, 14800, sw=10)
rect(9800, 12900, 10400, 14900, fill="#eee", sw=14)
# 南阳台
rect(12350, 13100, 12700, 13500, sw=12); circle(12525, 13300, 150)

# ================================================================== 房间名 + 面积（净空多边形）
room("主卧室", [(100,250),(4070,250),(4070,3660),(100,3660)], 2000, 1950)
room("主卫生间", [(4300,100),(7815,100),(7815,2400),(4300,2400)], 5450, 1250, 280)
room("过厅", [(4300,2550),(7880,2550),(7880,3640),(4300,3640)], 5000, 3150, 240)
room("衣帽间", [(7950,100),(10625,100),(10625,3620),(7950,3620)], 9300, 600, 280)
room("北阳台", [(10875,1400),(12800,1400),(12800,2325),(10875,2325)], 11850, 1800, 220, count=False)
room("家政多功能室", [(10955,2550),(12650,2550),(12650,5610),(10955,5610)], 11800, 3700, 220)
room("多功能室", [(1700,3860),(5600,3860),(5600,7490),(1700,7490),(1700,6841),(1450,6841),(1450,4815),(1700,4815)], 3600, 6300, note="开放式，东侧以保留剪力墙线划分")
room("休闲阳台", [(-150,4100),(1250,4100),(1250,11150),(-150,11150)], 550, 7600, 220, count=False)
room("客厅", [(1700,7750),(5600,7750),(5600,11350),(1700,11350),(1700,10451),(1450,10451),(1450,8425),(1700,8425)], 3650, 8250, note="开放式，东侧以保留剪力墙线划分")
room("西厨", [(7070,3760),(10625,3760),(10625,5610),(10955,5610),(10955,5830),(7070,5830)], 8300, 4420, 260, note="开放式，南侧以玄关墙线划分")
room("餐厅", [(5600,3860),(7070,3860),(7070,5830),(10084,5830),(10084,9550),(9505,9550),(9505,11350),(5600,11350)], 7950, 7000, note="含过厅双开门前通道")
room("玄关", [(10330,5830),(12650,5830),(12650,7440),(10330,7440)], 11500, 6500, 280)
room("储物/收纳", [(10276,7440),(11950,7440),(11950,9550),(10276,9550)], 11100, 8300, 220)
room("中厨", [(9700,9700),(12712,9700),(12712,12900),(10920,12900),(10920,11250),(9700,11250)], 11300, 10900, 280)
room("南阳台", [(10920,12900),(12712,12900),(12712,14010),(10920,14010)], 12250, 13800, 170, count=False)
room("卧室", [(100,11650),(4050,11650),(4050,14950),(100,14950)], 2000, 13300)
room("走道(西)", [(4250,11650),(5465,11650),(5465,12633),(4250,12633)], 4800, 12050, 170)
room("走道(东)", [(5555,11710),(7795,11710),(7795,12633),(5555,12633)], 6600, 12050, 190)
room("客卫生间A", [(4250,12763),(6060,12763),(6060,14950),(4250,14950)], 5150, 13700, 210)
room("客卫生间B", [(6250,12763),(7795,12763),(7795,14950),(6250,14950)], 7000, 13700, 210)
room("儿童卧室", [(7970,11750),(10650,11750),(10650,14950),(7970,14950)], 9200, 12550, 280)

# ================================================================== 外围尺寸链（原图标注）
def chain_h(y, xs, segs, above, total):
    x = xs; pts = [xs]
    line(xs, y, xs+sum(segs), y, sw=16)
    for s in segs: x += s; pts.append(x)
    for p in pts: line(p, y-110, p, y+110, sw=16); line(p-70, y+70, p+70, y-70, sw=22)
    for i, s in enumerate(segs):
        text((pts[i]+pts[i+1])/2, y-80 if above else y+300, str(s), 250, fill=C_AXIS)
    yt = y-800 if above else y+800
    line(xs, yt, xs+sum(segs), yt, sw=16)
    for p in (xs, xs+sum(segs)): line(p, yt-110, p, yt+110, sw=16); line(p-70, yt+70, p+70, yt-70, sw=22)
    text(xs+sum(segs)/2, yt-80 if above else yt+300, str(total), 250, fill=C_AXIS)
def chain_v(x, ys, segs, left, total):
    y = ys; pts = [ys]
    line(x, ys, x, ys+sum(segs), sw=16)
    for s in segs: y += s; pts.append(y)
    for p in pts: line(x-110, p, x+110, p, sw=16); line(x-70, p+70, x+70, p-70, sw=22)
    for i, s in enumerate(segs):
        text(x-80 if left else x+300, (pts[i]+pts[i+1])/2, str(s), 250, fill=C_AXIS, rotate=-90)
    xt = x-800 if left else x+800
    line(xt, ys, xt, ys+sum(segs), sw=16)
    for p in (ys, ys+sum(segs)): line(xt-110, p, xt+110, p, sw=16); line(xt-70, p+70, xt+70, p-70, sw=22)
    text(xt-80 if left else xt+300, ys+sum(segs)/2, str(total), 250, fill=C_AXIS, rotate=-90)
XS = [1300, 2900, 1900, 1700, 3000, 2100, 2950, 2700]
YS = [2400, 1300, 2000, 1900, 2650, 1250, 1400, 2300, 2150]
chain_h(-1300, 0, XS, True, 18550); chain_h(18650, 0, XS, False, 18550)
chain_v(-1300, 0, YS, True, 17350); chain_v(19850, 0, YS, False, 17350)
for i, x in enumerate(XA): circle(x, -2850, 230, fill="#fff"); text(x, -2760, str(i+1), 250)
for i, y in enumerate(YA): circle(-2850, y, 230, fill="#fff"); text(-2850, y+90, chr(ord("A")+i), 250)

# ================================================================== 标题 / 图例 / 比例尺 / 指北
nx, ny = 20500, 1500
add(f'<path d="M {nx} {ny-700} L {nx+250} {ny+300} L {nx} {ny+100} L {nx-250} {ny+300} Z" fill="#000"/>'); text(nx, ny+750, "北", 300, weight="bold")
text(X0+300, Y0+700, "深业世纪山谷 3C栋 04+05打通户型  建面约262㎡  平面图（高清重绘 v3：门窗、墙体逐一按原图复核）", 480, anchor="start", weight="bold")
text(X0+300, Y0+1250, "黑色外围尺寸链（mm）为开发商原图标注；灰色=墙段/洞口推算净长，蓝色=窗/玻璃推算长度，红色=门洞宽；房间面积为推算墙面围合的净面积（不含墙体），仅供参考，非测绘成果，非施工图。", 230, anchor="start", fill="#333")
text(X0+300, Y0+1650, "墙体按原图画法判读：白色填充→实墙（原建筑墙）；空心双线→新建隔墙（材质不明）；点状/空心矩形填充→柱/墙垛（疑似结构构件）；外围细线→玻璃窗/幕墙；阳台外缘双线→玻璃栏板。门扇/开启方向逐一按原图弧线复核。", 230, anchor="start", fill="#333")

lx, ly = 12900, 19600
def leg(i, draw, label):
    y = ly + i*430
    draw(y); text(lx+800, y+230, label, 220, anchor="start")
leg(0, lambda y: (shear(lx, y, lx+280, y+250), hollowbox(lx+320, y, lx+600, y+250)), "柱 / 墙垛（原图点状或空心矩形填充，疑似结构构件，非结构图）")
leg(1, lambda y: solid(lx, y, lx+600, y+250), "实墙（原图白色填充，原建筑墙体）")
leg(2, lambda y: light(lx, y, lx+600, y+200), "新建隔墙（原图空心双线，材质不明）")
leg(3, lambda y: glass(lx, y+120, lx+600, y+120), "外窗 / 玻璃门窗")
leg(4, lambda y: rail(lx, y+120, lx+600, y+120), "玻璃栏板")
leg(5, lambda y: hatch(lx, y, lx+600, y+250), "固定柜体")
leg(6, lambda y: rect(lx, y, lx+600, y+250, fill="url(#core)", stroke="none"), "公共区域（电梯厅 / 楼梯 / 管井）")
leg(7, lambda y: (door(lx, y+250, 300, "E", "ccw"), slide(lx+350, y+250, lx+600, y+250, lx+380, lx+520)), "平开门（弧线=开启方向，直线=门扇）/ 推拉门（细线+粗条）")

sbx, sby = 0, 19700
for i in range(5): rect(sbx+i*1000, sby, sbx+(i+1)*1000, sby+180, fill="#000" if i % 2 == 0 else "#fff", sw=15)
for i in range(6): text(sbx+i*1000, sby+480, f"{i}m", 220)

# 面积汇总
tx, ty = 0, 20900
indoor = sum(a for n, a, c in ROOMS if c); balc = sum(a for n, a, c in ROOMS if not c)
text(tx, ty, "面积汇总（推算净面积，不含墙体）", 260, anchor="start", weight="bold")
text(tx, ty+420, f"室内各空间合计 ≈ {indoor:.1f} ㎡（含走道，不含阳台/空调机位/管井）", 230, anchor="start")
text(tx, ty+800, f"阳台合计 ≈ {balc:.1f} ㎡（休闲阳台 + 北阳台 + 南阳台）", 230, anchor="start")
text(tx, ty+1180, f"外轮廓轴线面积（含公共走道/电梯厅/楼梯）18.55 m × 17.35 m ≈ {18.55*17.35:.1f} ㎡", 230, anchor="start")
text(tx, ty+1560, "建筑面积 262 ㎡ 为含公摊口径，不能与上述净面积直接相减得到公摊；精确套内面积以《房屋测绘报告》为准。", 230, anchor="start", fill="#333")
text(tx, ty+2000, "原图来源：开发商宣传户型图（用户提供）。重绘：2026-11，脚本 重绘脚本_draw_262_plan_v3.py。", 200, anchor="start", fill="#555")

add('</svg>')
svg = "\n".join(out)
base = os.path.join(OUT, "3C_262_0405打通_高清重绘_带尺寸")
open(base + ".svg", "w", encoding="utf-8").write(svg)
cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=base + ".png", output_width=7000)
cairosvg.svg2pdf(bytestring=svg.encode("utf-8"), write_to=base + ".pdf")
json.dump([{"room": n, "area_m2": round(a, 2), "indoor": c} for n, a, c in ROOMS],
          open(os.path.join(OUT, "262_room_areas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for n, a, c in ROOMS: print(f"{n:8s} {a:6.2f} ㎡ {'' if c else '(阳台)'}")
print(f"indoor {indoor:.2f}  balcony {balc:.2f}")
