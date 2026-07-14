# -*- coding: utf-8 -*-
"""
Фон секции «Небо, полное миров»: снимок РЕАЛЬНОГО купола-филлотаксиса, сделанный
камерой, поставленной ВНУТРЬ купола вплотную к поверхности.

Метод (не выдуманный узор, а тот же, что на своде):
  1. Берём ТЕ ЖЕ зёрна, что в make_domes.phyllo: N=1400, золотой угол,
     r=sqrt(i/N)*0.97, размер sz=0.008+0.018*(i/N), тёплый градиент цвета.
  2. Купол = полусфера (обратная равнопромежуточной Dome-Master проекции):
     диск-радиус r → полярный угол theta=r*(pi/2); зерно садится на поверхность.
  3. Ставим камеру внутри купола на малом расстоянии от целевой точки P0,
     смотрим на P0 вдоль нормали. Перспективная (pinhole) проекция каждого зерна:
     ближние — крупные в центре, дальние — мельче и к краям, косые гаснут.
  4. В кадр попадает ~5% площади свода → десятки зёрен, разрежённость как на своде.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_phyllo_bg.py
"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
GROUND = "#0e0b18"                                   # тёмный грунт свода (как в phyllo)
def hx(c): c=c.lstrip("#"); return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255.0
def norm(v): return v/ (np.linalg.norm(v)+1e-12)

# ── параметры свода = точь-в-точь make_domes.phyllo ──
N  = 1400
GA = np.pi*(3-np.sqrt(5))
RD = 1.0                                             # радиус купола
Wpx, Hpx = 2560, 1440
ASPECT = Wpx/Hpx

# ── постановка камеры внутри купола ──
theta0 = 0.98                                        # куда наведён объектив (полярный угол цели)
phi0   = 0.55
DCAM   = 0.34*RD                                     # камера у поверхности (широкий угол → «внутри купола»)
FOV_X  = np.radians(95)                              # широкоугольный объектив: сильная перспектива
SEED_K = 1.18                                        # 3D-радиус зерна ≈ sz*SEED_K (подгон разрежения)

def seed_world(i):
    r = np.sqrt(i/N)*0.97
    if r*r > 0.985: return None
    a = i*GA
    u, v = r*np.cos(a), r*np.sin(a)                  # диск Dome-Master
    theta = r*(np.pi/2)                              # обратная проекция → полусфера
    P = RD*np.array([np.sin(theta)*np.cos(a),
                     np.sin(theta)*np.sin(a),
                     np.cos(theta)])
    sz = 0.008+0.018*(i/N)
    warm = np.clip(hx("#c98a2a")*(0.5+0.6*(i/N)) + hx("#f0d48a")*(1-i/N)*0.5, 0, 1)
    return P, sz, warm, (i/N)

def build():
    # цель и базис камеры
    P0 = RD*np.array([np.sin(theta0)*np.cos(phi0),
                      np.sin(theta0)*np.sin(phi0),
                      np.cos(theta0)])
    n_out = norm(P0)                                 # внешняя нормаль полусферы
    C = P0 - n_out*DCAM                              # камера внутри, у самой поверхности
    fwd = norm(P0 - C)                               # взгляд — на поверхность (== n_out)
    up0 = np.array([0,0,1.0])
    right = norm(np.cross(fwd, up0)); up = np.cross(right, fwd)
    fpx = (Wpx/2)/np.tan(FOV_X/2)                    # фокус в пикселях

    fig = plt.figure(figsize=(Wpx/200, Hpx/200), dpi=200)
    fig.patch.set_facecolor(GROUND)
    ax = fig.add_axes([0,0,1,1]); ax.axis("off")
    ax.set_xlim(0, Wpx); ax.set_ylim(0, Hpx); ax.set_aspect("equal")
    ax.add_patch(plt.Rectangle((0,0), Wpx, Hpx, fc=hx(GROUND), ec="none", zorder=0))

    items = []
    for i in range(N):
        s = seed_world(i)
        if s is None: continue
        P, sz, warm, depth = s
        d = P - C
        zc = float(np.dot(d, fwd))
        if zc <= 0.02: continue                      # позади камеры
        ni = -norm(P)                                # нормаль внутренней поверхности → к центру
        cos_ob = float(np.dot(norm(C-P), ni))        # 1 в лоб, →0 по касательной
        if cos_ob <= 0.06: continue                  # смотрит от нас
        xc = float(np.dot(d, right)); yc = float(np.dot(d, up))
        px = Wpx/2 + fpx*xc/zc; py = Hpx/2 + fpx*yc/zc
        if not (-0.15*Wpx < px < 1.15*Wpx and -0.15*Hpx < py < 1.15*Hpx): continue
        scale = fpx/zc
        Rmaj = sz*SEED_K*scale                       # экранный радиус (перспектива)
        Rmin = Rmaj*np.clip(cos_ob, 0.14, 1.0)       # ракурс: сжатие косых зёрен в эллипс
        # ориентация малой оси = проекция внешней нормали на плоскость кадра
        no = norm(P)
        nx = float(np.dot(no, right)); nyv = float(np.dot(no, up))
        ang = np.degrees(np.arctan2(nyv, nx))
        # свет: тёплый градиент × ракурс × глубина (дальние глуше)
        lit = (0.40 + 0.72*cos_ob) * (0.82 + 0.18*(1-depth))
        col = np.clip(warm*lit, 0, 1)
        items.append((zc, px, py, Rmaj, Rmin, ang, col, cos_ob, warm, lit))

    items.sort(key=lambda t: -t[0])                  # дальние сначала (painter)
    for zc, px, py, Rmaj, Rmin, ang, col, cos_ob, warm, lit in items:
        if Rmaj < 0.6: continue
        ax.add_patch(Ellipse((px,py), 2*Rmaj, 2*Rmin, angle=ang,
                             fc=col, ec=hx("#0b0a0f"), lw=max(0.4, Rmaj*0.05), zorder=2))
        # блик-стад к свету (объём зерна) — сдвиг к верх-левому
        hlc = np.clip(col*1.4 + hx("#f0d48a")*0.28, 0, 1)
        ax.add_patch(Ellipse((px - Rmaj*0.26, py + Rmaj*0.30),
                             Rmaj*0.60, Rmin*0.60, angle=ang,
                             fc=hlc, ec="none", alpha=0.9*np.clip(cos_ob,0,1), zorder=3))

    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    img = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h,w,4)[...,:3].copy()
    plt.close(fig)
    print("seeds in frame:", len(items), "= %.1f%% of dome" % (100*len(items)/N))
    return Image.fromarray(img, "RGB"), (Wpx/2, Hpx/2)

def photo(im, focus):
    """DoF-расфокус к краям, виньетка, экспозиция вниз — как реальный макро-снимок."""
    W,H = im.size
    blur = im.filter(ImageFilter.GaussianBlur(8))
    yy,xx = np.mgrid[0:H,0:W].astype(float)
    fx,fy = focus
    d = np.hypot((xx-fx)/W, (yy-fy)/H)
    m = np.clip((d-0.16)/0.40, 0, 1)**1.4
    out = Image.composite(blur, im, Image.fromarray((m*255).astype(np.uint8), "L"))
    a = np.asarray(out, float)
    vig = np.clip(1.0 - 0.55*(d**1.5), 0.30, 1.0)[...,None]
    a = a*vig*0.92
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8), "RGB")

if __name__ == "__main__":
    im, focus = build()
    im = photo(im, focus)
    p = os.path.join(OUT, "bg_phyllo_close.jpg")
    im.save(p, quality=88, subsampling=1, dpi=(170,170))
    print("ok", os.path.basename(p), im.size)
