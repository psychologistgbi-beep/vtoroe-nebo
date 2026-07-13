# -*- coding: utf-8 -*-
"""
ОБРАЗЕЦ: свод, скомпонованный по законам графики проекта (THEORY.md), фронтально.
Т1 вынесенный центр · Т2 честная асимметричная сетка (полюс вне тела) ·
Т3 одна зеркальная ось · Т5 тон = кривизна · Т8 рамка. Без наклона, без железа.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_law.py
"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import LineCollection
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"img")
F,X0,A=360.0,336.0,300.0
VOID="#08070e"
def hx(c):
    c=c.lstrip("#");return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255.0
def _J1(x):
    ax=np.abs(x);y=x*x
    p1=x*(72362614232.0+y*(-7895059235.0+y*(242396853.1+y*(-2972611.439+y*(15704.48260+y*(-30.16036606))))))
    q1=144725228442.0+y*(2300535178.0+y*(18583304.74+y*(99447.43394+y*(376.9991397+y*1.0))))
    z=8.0/np.where(ax==0,1e-9,ax);y2=z*z;xx=ax-2.356194491
    p2=1.0+y2*(0.183105e-2+y2*(-0.3516396496e-4+y2*(0.2457520174e-5+y2*(-0.240337019e-6))))
    q2=0.04687499995+y2*(-0.2002690873e-3+y2*(0.8449199096e-5+y2*(-0.88228987e-6+y2*0.105787412e-6)))
    large=np.sqrt(0.636619772/np.where(ax==0,1e-9,ax))*(np.cos(xx)*p2-z*np.sin(xx)*q2)*np.sign(x)
    return np.where(ax<8.0,p1/q1,large)

def law_beam():
    N=760;xs=np.linspace(-1,1,N);U,Vv=np.meshgrid(xs,xs);R=np.hypot(U,Vv)
    disc=R<=0.995
    xc=U*A;yc=Vv*A;xa=X0+xc
    # --- Т5: тон = кривизна. Глубина растёт с расстоянием от РОДИТЕЛЬСКОЙ оси (xa,yc).
    rho=np.hypot(xa,yc)
    depth=(rho-rho[disc].min())/(rho[disc].max()-rho[disc].min())   # 0 у ближней кромки → 1 у дальней
    curv=1.0-0.62*depth**1.3                                        # тьма к дальней (правой) кромке
    # --- Т1: кольца слуха вокруг ВЫНЕСЕННОГО фокуса (смещён к вырезу, off-center) ---
    u0,v0=-0.34,0.0
    du,dv=(U-u0),(Vv-v0)
    # Т3: одна зеркальная ось (горизонталь v=0); кома офсета — сжатие по стороне фида
    coma=1.0+0.28*np.clip(-du,0,1.4)
    d=np.sqrt((du*coma)**2+(dv*1.06)**2)
    k=12.5;x=k*d+1e-6
    P=(2*_J1(x)/x)**2
    PdB=10*np.log10(np.clip(P,1e-4,None));val=np.clip((PdB+40)/40,0,1)
    val=val*curv                                                   # тон несёт кривизну
    # цветоращивание (тёплое золото по тёмному)
    c_lo=hx("#0a0a14");c_mid=hx("#7a4c18");c_hi=hx("#ffe6a0")
    img=np.zeros((N,N,4))
    for ch in range(3):
        img[...,ch]=np.where(val<0.5,c_lo[ch]+(c_mid[ch]-c_lo[ch])*(val/0.5),
                             c_mid[ch]+(c_hi[ch]-c_mid[ch])*((val-0.5)/0.5))
    img[...,3]=np.where(disc,1.0,0.0)

    fig=plt.figure(figsize=(8,8),dpi=170);fig.patch.set_facecolor(VOID)
    ax=fig.add_axes([0,0,1,1]);ax.set_xlim(-1.08,1.08);ax.set_ylim(-1.08,1.08)
    ax.set_aspect("equal");ax.axis("off")
    ax.imshow(img,extent=[-1,1,-1,1],origin="lower",zorder=2,interpolation="bilinear")

    # --- Т2: ЧЕСТНАЯ сетка — параллели×меридианы РОДИТЕЛЬСКОГО параболоида.
    # полюс (родительская ось) вне тела: в аперт. координатах u_pole=-X0/A=-1.12 ---
    up=-X0/A
    clipc=Circle((0,0),0.995,transform=ax.transData)
    segs=[]
    # параллели: rho=const → окружности с центром (up,0)
    for rr in np.linspace(120,540,8):
        aa=np.linspace(-np.pi,np.pi,240)
        cu=up+(rr/A)*np.cos(aa);cv=(rr/A)*np.sin(aa)
        m=(cu*cu+cv*cv)<=0.995**2
        if m.sum()>2: segs.append(np.column_stack([cu[m],cv[m]]))
    # меридианы: лучи из полюса (up,0)
    for ang in np.linspace(-0.9,0.9,11):
        t=np.linspace(0,2.4,120)
        cu=up+t*np.cos(ang);cv=t*np.sin(ang)
        m=(cu*cu+cv*cv)<=0.995**2
        if m.sum()>2: segs.append(np.column_stack([cu[m],cv[m]]))
    lc=LineCollection(segs,colors=hx("#caa24c"),linewidths=0.5,alpha=0.16,zorder=3)
    lc.set_clip_path(clipc);ax.add_collection(lc)

    # Т8: рамка + вынесенный центр-указатель (проекция фокуса), off-center
    ax.add_patch(Circle((0,0),0.997,fill=False,ec=hx("#caa24c"),lw=1.4,alpha=0.4,zorder=6))
    ax.add_patch(Circle((u0,v0),0.012,fc=hx("#fff2cf"),ec="none",zorder=6))
    fn=os.path.join(OUT,"dome_law_beam.jpg")
    fig.savefig(fn,facecolor=VOID);plt.close(fig);print("ok",fn)

law_beam();print("done")
