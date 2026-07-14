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
        m=re.search(r'dish_((?:dp|nv|wk25|fn)_[a-z0-9]+)',sp)
        stem=m.group(1) if m else "x"
        ax=fig.axes[0]
        for coll in list(ax.collections):
            try: coll.set_clip_path(Circle((0,0),A,transform=ax.transData))
            except Exception: pass
        name=DOME.get(stem,stem)
        planet_frame(ax, warm=WARM.get(name,"#dfeafa"))
        fig._orig_savefig(os.path.join(OUT,f"dome_{name}.jpg"),facecolor=VOID)
        plt.close(fig); print("ok dome_%s (deep %s)"%(name,stem))
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
      "muqarnas":"#f0d091","mandala":"#e8d29a","san_marco":"#ffe6a0",
      "portal_1":"#cfe0f5","portal_2":"#fff2c8","portal_3":"#fff2c8"}
# cogos stem -> site dome name
DOME={"dp_tesserae":"san_marco","dp_muqarnas":"muqarnas","dp_mandala":"mandala",
      "dp_portal":"portal_2","fn_portal":"portal_3","wk25_portal":"portal_1"}

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

import make_final as MF                                   # fn_portal — тоже через D.PV

REG={}
for w in ("percol","vitel","frost","mayatnik","nabor","chern"):
    REG[w]=getattr(C,w)                                  # chaos: сохраняются через C.save
for w in ("tesserae","muqarnas","mandala","portal"):
    REG[w]=getattr(D,w)                                  # deep: сохраняются через fig.savefig-обёртку
REG["fn_portal"]=lambda: MF.portal()                     # Портал III

# ── Портал I = wk25: код make_portal, но сетка пересчитана ФРОНТАЛЬНО ──
def render_wk25():
    import make_portal as MP
    from matplotlib.collections import PolyCollection
    MP.Rm = MP.rotm(0,0)                                  # proj() -> фронтально (ангелы)
    q=[];uu=[];vv=[];nd=[];dep=[]
    for i in range(MP.NR-1):
        for j in range(MP.NT-1):
            idx=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
            xs=[MP.Xc[a,b] for a,b in idx]; ys=[MP.Yc[a,b] for a,b in idx]
            nvc=np.array([np.mean([MP.Nx[a,b] for a,b in idx]),
                          np.mean([MP.Ny[a,b] for a,b in idx]),
                          np.mean([MP.Nz[a,b] for a,b in idx])])
            nvc=nvc/np.linalg.norm(nvc)
            q.append(np.column_stack([xs,ys]))
            uu.append(np.mean([MP.Xc[a,b] for a,b in idx])/MP.A)
            vv.append(np.mean([MP.Yc[a,b] for a,b in idx])/MP.A)
            nd.append(float(np.clip(nvc@MP.L,0,1))); dep.append(np.mean([MP.Zc[a,b] for a,b in idx]))
    o=np.argsort(dep)
    MP.QUADS=[q[k] for k in o]; MP.UU=np.array(uu)[o]; MP.VV=np.array(vv)[o]
    MP.ND=np.array(nd)[o]; MP.RAD=np.sqrt(MP.UU**2+MP.VV**2); MP.ANG=np.arctan2(MP.VV,MP.UU)
    col,em=MP.portal_field()
    shade=(0.34+(0.8-0.34)*MP.ND)[:,None]; fc=np.clip(col*shade+em,0,1)
    fig,ax=newfig_frontal("#0e0f13")
    pc=PolyCollection(MP.QUADS,facecolors=fc,edgecolors=fc,linewidths=0.4,zorder=2)
    ax.add_collection(pc)
    rings=[(0.86,34,4.6),(0.70,28,4.0),(0.55,22,3.4),(0.42,17,2.8),(0.30,12,2.2),(0.20,8,1.7)]
    for ri,(r,n,s) in enumerate(rings):
        off=ri*0.5
        for k in range(n):
            aa=2*np.pi*k/n+off; u=r*np.cos(aa)*0.98; v=r*np.sin(aa)*1.0
            x,y,sc=MP.proj(u,v)
            near=np.exp(-(r**2)/0.25); c=MP.hx("#1a1c22")*near+MP.hx("#e9dcb0")*(1-near)
            MP.angel(ax,x,y,s*sc,np.arctan2(-v,-u)-np.pi/2,c,alpha=0.92)
    for coll in list(ax.collections):
        try: coll.set_clip_path(Circle((0,0),A,transform=ax.transData))
        except Exception: pass
    planet_frame(ax, warm="#cfe0f5")
    fig._orig_savefig(os.path.join(OUT,"dome_portal_1.jpg"),facecolor=VOID)
    plt.close(fig); print("ok dome_portal_1 (wk25 фронтально)")
REG["wk25"]=render_wk25

if __name__=="__main__":
    args=sys.argv[1:] or list(REG)
    for a in args:
        REG[a]()
    print("done")
