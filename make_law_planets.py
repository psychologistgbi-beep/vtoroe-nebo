# -*- coding: utf-8 -*-
"""
Планеты из ТОГО ЖЕ кода и математики cogos: ставим проекцию make_deep фронтально
(Rm=identity), подменяем фон/рамку/сохранение — и гоняем оригинальные генераторы
(make_chaos_dish / make_native / make_deep) как планеты. Без наклона, без железа.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_law_planets.py [tag...]
"""
import sys, os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
SK="/Users/gaidabura/Documents/Agency/Projects/overton-window/satellite-dish/sketches"
CR="/Users/gaidabura/Documents/Agency/Projects/overton-window/chaos-rospis/sketches"
sys.path.insert(0,SK); sys.path.insert(0,CR)
import make_deep as D
D.Rm = D.rotm(0,0)                 # фронтальная проекция (в мм апертуры)
A=D.A; W=A*1.14
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
VOID="#08070e"; rng=np.random.default_rng(41)
def hx(c): c=c.lstrip("#"); return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255.0

import re
def _finalize_factory(fig):
    def _finalize(path,*a,**k):
        sp=str(path)
        if "zoom" in sp: return                      # у portal есть второй кадр-зум — пропускаем
        m=re.search(r'dish_(?:dp|nv|wk25|fn)_([a-z0-9]+)',sp)
        tag=m.group(1) if m else "x"
        ax=fig.axes[0]
        for coll in list(ax.collections):
            try: coll.set_clip_path(Circle((0,0),A,transform=ax.transData))
            except Exception: pass
        planet_frame(ax, warm=WARM.get(tag,"#dfeafa"))
        name=DOME.get(tag,tag)
        fig._orig_savefig(os.path.join(OUT,f"dome_{name}.jpg"),facecolor=VOID)
        plt.close(fig); print("ok dome_%s (deep %s)"%(name,tag))
    return _finalize
def newfig_frontal(bg):
    fig=plt.figure(figsize=(8,8),dpi=170); fig.patch.set_facecolor(VOID)
    ax=fig.add_axes([0,0,1,1]); ax.set_xlim(-W,W); ax.set_ylim(-W,W)
    ax.set_aspect("equal"); ax.axis("off")
    fig._orig_savefig=fig.savefig
    fig.savefig=_finalize_factory(fig)
    return fig,ax
def flat_disc(ax,col,vig=0.0,lite=None,amb=0.5,hi=0.8):   # для make_chaos_dish.flat_base(col-строка)
    ax.add_patch(Circle((0,0),A,fc=hx(col),ec="none",zorder=1))
def flat_disc_fn(ax,colfn,amb=0.32,hi=0.85):              # для make_deep.base(colfn)
    try: c=np.clip(np.asarray(colfn(np.array([0.0]),np.array([0.0]),np.array([0.0])))[0],0,1)
    except Exception: c=hx("#141018")
    ax.add_patch(Circle((0,0),A,fc=c,ec="none",zorder=1))

def planet_frame(ax, warm="#cfe0f5", dark=0.6):
    N=520; xs=np.linspace(-W,W,N); xx,yy=np.meshgrid(xs,xs); r=np.hypot(xx,yy)/A
    inside=r<=1.0; z=np.sqrt(np.clip(1-np.clip(r,0,1)**2,0,1))
    Lx,Ly,Lz=-0.42,0.52,0.74; n=(Lx*Lx+Ly*Ly+Lz*Lz)**.5; Lx,Ly,Lz=Lx/n,Ly/n,Lz/n
    ndotl=np.clip((xx/A)*Lx+(yy/A)*Ly+z*Lz,0,1); shade=0.42+0.58*ndotl
    dA=np.where(inside,np.clip((1-shade)*(0.45+dark*0.6),0,0.86),0.0)
    di=np.zeros((N,N,4)); di[...,3]=dA
    ax.imshow(di,extent=[-W,W,-W,W],origin="lower",zorder=30,interpolation="bilinear")
    hiA=np.where(inside,np.clip((shade-0.80)*2.4,0,0.32),0.0)
    hii=np.zeros((N,N,4)); hii[...,:3]=hx(warm); hii[...,3]=hiA
    ax.imshow(hii,extent=[-W,W,-W,W],origin="lower",zorder=31,interpolation="bilinear")
    M=170; sx=(rng.random(M)*2-1)*W; sy=(rng.random(M)*2-1)*W; k=(np.hypot(sx,sy)/A)>1.04
    for xs_,ys_ in zip(sx[k],sy[k]):
        ax.scatter([xs_],[ys_],s=float(rng.random()*2.4+0.3),
                   c=[[0.91,0.925,0.96,float(rng.random()*0.6+0.25)]],zorder=0,linewidths=0)
    atmo=np.where(r>0.85,np.exp(-((r-1.005)/0.055)**2)*(0.20+0.80*ndotl),0.0)
    atm=np.zeros((N,N,4)); atm[...,:3]=hx("#bcd0f0"); atm[...,3]=np.clip(atmo*0.5,0,0.5)
    ax.imshow(atm,extent=[-W,W,-W,W],origin="lower",zorder=33,interpolation="bilinear")

WARM={"percol":"#dfeafa","vitel":"#f4d98f","frost":"#cfe0f5","mayatnik":"#f0d692",
      "nabor":"#e5b26a","chern":"#e8eaef","reaction":"#c8f2e0","beam":"#cfeef5",
      "muqarnas":"#f0d091","mandala":"#e8d29a","tesserae":"#ffe6a0",
      "portal":"#fff2c8","pozzo":"#fff2c8"}
# cogos tag -> site dome name
DOME={"tesserae":"san_marco","portal":"portal_2","pozzo":"portal_1"}

# общие патчи проекции/фона/рамки
D.newfig=newfig_frontal
D.finish=lambda ax,bg:None
D.caption=lambda *a,**k:None
D.base=flat_disc_fn                      # make_deep.base(colfn) -> плоский диск

def wrap_save(fig,tag,bg):               # для make_chaos_dish.save(fig,tag,bg)
    ax=fig.axes[0]
    for coll in list(ax.collections):
        try: coll.set_clip_path(Circle((0,0),A,transform=ax.transData))
        except Exception: pass
    planet_frame(ax, warm=WARM.get(tag,"#dfeafa"))
    fig._orig_savefig(os.path.join(OUT,f"dome_{DOME.get(tag,tag)}.jpg"),facecolor=VOID)
    plt.close(fig); print("ok dome_%s (chaos %s)"%(DOME.get(tag,tag),tag))

import make_chaos_dish as C
C.flat_base=flat_disc; C.cap=lambda *a,**k:None; C.save=wrap_save

REG={}
for w in ("percol","vitel","frost","mayatnik","nabor","chern"):
    REG[w]=getattr(C,w)                                  # chaos: сохраняются через C.save
for w in ("tesserae","muqarnas","mandala","portal","pozzo"):
    REG[w]=getattr(D,w)                                  # deep: сохраняются через fig.savefig-обёртку

if __name__=="__main__":
    args=sys.argv[1:] or list(REG)
    for a in args:
        REG[a]()
    print("done")
