# -*- coding: utf-8 -*-
"""
Фавикон «ВТОРОЕ НЕБО»: золотая филлотаксис-сфера-окулюс на воиде + красный клин.
Из ОДНОГО расчёта: favicon.svg (вектор, primary) + PNG-фолбэки (32, 180 apple-touch, 512).
Тот же закон филлотаксиса и палитра, что у hero.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_favicon.py
"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VOID="#08070e"; GOLD_HI="#f4dc95"; GOLD="#c9932f"; GOLD_LO="#5e3f14"; RED="#d85138"
def hx(c): c=c.lstrip("#"); return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255.0

# ── общий расчёт: филлотаксис-зёрна на сфере, свет сверху-слева ──
N=48; GA=np.pi*(3-np.sqrt(5))
Lx,Ly,Lz=-0.42,0.52,0.74; ln=(Lx*Lx+Ly*Ly+Lz*Lz)**.5; Lx,Ly,Lz=Lx/ln,Ly/ln,Lz/ln
SEEDS=[]
for i in range(N):
    r=np.sqrt((i+0.5)/N)*0.84; a=i*GA
    u,v=r*np.cos(a), r*np.sin(a)
    z=np.sqrt(max(1-r*r,0))
    ndotl=max(u*Lx+v*Ly+z*Lz,0)          # ламберт на сфере
    lit=0.20+0.80*ndotl                  # сильнее терминатор → читается 3D-шар
    sz=0.040+0.050*(i/N)                 # зерно растёт к краю
    SEEDS.append((u,v,sz,lit))

def lerp(c0,c1,t): return c0+(c1-c0)*t
def dot_hex(lit):
    c = lerp(hx(GOLD_LO),hx(GOLD),min(lit/0.55,1)) if lit<0.55 else lerp(hx(GOLD),hx(GOLD_HI),(lit-0.55)/0.45)
    return "#%02x%02x%02x"%tuple(int(round(x*255)) for x in np.clip(c,0,1))

# ── SVG (вектор) ──
def emit_svg():
    S=64; C=S/2; R=25.5
    P=[]
    P.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">')
    P.append('<defs>')
    P.append(f'<radialGradient id="sky" cx="34%" cy="30%" r="80%">'
             f'<stop offset="0%" stop-color="#12101c"/><stop offset="100%" stop-color="{VOID}"/></radialGradient>')
    P.append(f'<radialGradient id="orb" cx="34%" cy="30%" r="78%">'
             f'<stop offset="0%" stop-color="#241a10"/><stop offset="62%" stop-color="#140f0a"/>'
             f'<stop offset="100%" stop-color="#050409"/></radialGradient>')
    P.append('</defs>')
    P.append(f'<rect x="0" y="0" width="{S}" height="{S}" rx="14" fill="url(#sky)"/>')
    P.append(f'<circle cx="{C}" cy="{C}" r="{R}" fill="url(#orb)"/>')
    # зёрна филлотаксиса
    for u,v,sz,lit in SEEDS:
        cx=C+u*R; cy=C-v*R; rr=sz*R
        P.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rr:.2f}" fill="{dot_hex(lit)}"/>')
    # тонкий тёплый обод-окулюс
    P.append(f'<circle cx="{C}" cy="{C}" r="{R}" fill="none" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1.1"/>')
    # красный клин (Лисицкий) — фирменный акцент, сидит НА ободе снизу-справа
    ang=np.radians(-34); ex,ey=C+R*np.cos(ang), C-R*np.sin(ang)   # точка на ободе
    wl,wh=8.5,7.0; bx,by=ex-wl*0.34, ey
    P.append(f'<polygon points="{bx:.1f},{by-wh/2:.1f} {bx+wl:.1f},{by:.1f} {bx:.1f},{by+wh/2:.1f}" fill="{RED}"/>')
    P.append('</svg>')
    open(os.path.join(HERE,"favicon.svg"),"w").write("\n".join(P))
    print("ok favicon.svg")

# ── PNG (тот же дизайн, matplotlib) ──
def emit_png(px):
    fig=plt.figure(figsize=(px/100,px/100),dpi=100); ax=fig.add_axes([0,0,1,1])
    ax.set_xlim(-1,1); ax.set_ylim(-1,1); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_alpha(0)
    # скруглённый тёмный тайл
    ax.add_patch(FancyBboxPatch((-1,-1),2,2,boxstyle="round,pad=0,rounding_size=0.44",
                 fc=hx(VOID),ec="none",mutation_aspect=1,zorder=0))
    Rn=0.80
    ax.add_patch(Circle((0,0),Rn,fc=hx("#140f0a"),ec="none",zorder=1))
    # мягкий светлый блик у подсолнечной точки
    ax.add_patch(Circle((-0.24,0.30),Rn*0.9,fc=hx("#241a10"),ec="none",alpha=0.6,zorder=1))
    for u,v,sz,lit in SEEDS:
        ax.add_patch(Circle((u*Rn,v*Rn),sz*Rn,fc=hx(dot_hex(lit)),ec="none",zorder=2))
    ax.add_patch(Circle((0,0),Rn,fill=False,ec=hx(GOLD),lw=max(px/64*1.1,0.6),alpha=0.55,zorder=3))
    # красный клин — сидит на ободе снизу-справа
    ang=np.radians(-34); ex,ey=Rn*np.cos(ang),Rn*np.sin(ang); wl,wh=0.26,0.22; bx=ex-wl*0.34
    ax.add_patch(Polygon([(bx,ey+wh/2),(bx+wl,ey),(bx,ey-wh/2)],closed=True,fc=hx(RED),ec="none",zorder=4))
    fig.savefig(os.path.join(HERE,f"_fav_{px}.png"),transparent=True,dpi=100)
    plt.close(fig)

if __name__=="__main__":
    emit_svg()
    emit_png(512)
    im=Image.open(os.path.join(HERE,"_fav_512.png")).convert("RGBA")
    im.resize((180,180),Image.LANCZOS).save(os.path.join(HERE,"apple-touch-icon.png"))
    im.resize((32,32),Image.LANCZOS).save(os.path.join(HERE,"favicon-32.png"))
    im.resize((16,16),Image.LANCZOS).save(os.path.join(HERE,"favicon-16.png"))
    im.save(os.path.join(HERE,"favicon-512.png"))
    os.remove(os.path.join(HERE,"_fav_512.png"))
    print("ok PNGs: apple-touch-icon(180), favicon-32, favicon-16, favicon-512")
