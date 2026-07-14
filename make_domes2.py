# -*- coding: utf-8 -*-
"""
КУПОЛА, набор 2: слух, живая кожа, Сан-Марко, мукарны, мандала, Портал ×3.
Использует helpers из make_domes.py. Без «железа», без текста, заполняют свод.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_domes2.py [tag...]
"""
import sys, numpy as np
import make_domes as M
from matplotlib.patches import Circle
from matplotlib.collections import PolyCollection, LineCollection
hx=M.hx; clip=M.clip; base=M.base; frame=M.frame; newdome=M.newdome; save=M.save; rng=M.rng

def _J1(x):
    ax=np.abs(x); small=ax<8.0
    y=x*x
    p1=x*(72362614232.0+y*(-7895059235.0+y*(242396853.1+y*(-2972611.439+y*(15704.48260+y*(-30.16036606))))))
    q1=144725228442.0+y*(2300535178.0+y*(18583304.74+y*(99447.43394+y*(376.9991397+y*1.0))))
    z=8.0/np.where(ax==0,1e-9,ax); y2=z*z; xx=ax-2.356194491
    p2=1.0+y2*(0.183105e-2+y2*(-0.3516396496e-4+y2*(0.2457520174e-5+y2*(-0.240337019e-6))))
    q2=0.04687499995+y2*(-0.2002690873e-3+y2*(0.8449199096e-5+y2*(-0.88228987e-6+y2*0.105787412e-6)))
    large=np.sqrt(0.636619772/np.where(ax==0,1e-9,ax))*(np.cos(xx)*p2-z*np.sin(xx)*q2)*np.sign(x)
    return np.where(small,p1/q1,large)

def _ramp(val,stops):
    # stops: list of (pos,hexcol); val in 0..1
    N=val.shape; out=np.zeros(N+(3,))
    for ch in range(3):
        xs=[s[0] for s in stops]; ys=[hx(s[1])[ch] for s in stops]
        out[...,ch]=np.interp(val,xs,ys)
    return out

# ── АВТОПОРТРЕТ СЛУХА — концентрические кольца диаграммы (дифракция) ──
def beam():
    fig,ax=newdome(); base(ax,"#06131a")
    N=620; xs=np.linspace(-1,1,N); xx,yy=np.meshgrid(xs,xs); rr=np.hypot(xx,yy)
    k=11.0; x=k*rr+1e-6
    P=(2*_J1(x)/x)**2
    PdB=10*np.log10(np.clip(P,1e-4,None))
    val=np.clip((PdB+40)/40,0,1)
    rgb=_ramp(val,[(0.0,"#06131a"),(0.5,"#12586a"),(0.8,"#3fb2c2"),(1.0,"#dff4f8")])
    img=np.zeros((N,N,4)); img[...,:3]=rgb; img[...,3]=1.0
    clip(ax, ax.imshow(img,extent=[-1,1,-1,1],origin="lower",zorder=3,interpolation="bilinear"))
    ax.contour(xx,yy,PdB,levels=[-3],colors="#dff4f8",linewidths=1.3,zorder=5)
    frame(ax, warm="#cfeef5", ring="#3fb2c2", glow=0.0, rib=False, dark=0.34)
    save(fig,"beam")

# ── ЖИВАЯ КОЖА — реакция-диффузия Грея–Скотта (Тьюринг) ──
def reaction():
    fig,ax=newdome(); base(ax,"#07201b")
    N=230; U=np.ones((N,N)); V=np.zeros((N,N))
    for _ in range(28):
        i=rng.integers(24,N-24); j=rng.integers(24,N-24)
        U[i-3:i+4,j-3:j+4]=0.5; V[i-3:i+4,j-3:j+4]=0.25
    Du,Dv,f,k=0.16,0.08,0.0545,0.062
    for _ in range(5200):
        lu=(np.roll(U,1,0)+np.roll(U,-1,0)+np.roll(U,1,1)+np.roll(U,-1,1)-4*U)
        lv=(np.roll(V,1,0)+np.roll(V,-1,0)+np.roll(V,1,1)+np.roll(V,-1,1)-4*V)
        uvv=U*V*V; U+=Du*lu-uvv+f*(1-U); V+=Dv*lv+uvv-(f+k)*V
    field=(V-V.min())/(np.ptp(V)+1e-9)
    rgb=_ramp(field,[(0.0,"#07201b"),(0.4,"#0f5a4c"),(0.7,"#2fae90"),(1.0,"#c8f2e0")])
    img=np.zeros((N,N,4)); img[...,:3]=rgb; img[...,3]=1.0
    clip(ax, ax.imshow(img,extent=[-1,1,-1,1],origin="lower",zorder=3,interpolation="bilinear"))
    frame(ax, warm="#c8f2e0", ring="#2fae90", glow=0.22, rib=False, dark=0.45)
    save(fig,"reaction")

# ── МАНДАЛА — фиолетово-золотая тонкая решётка (по dp_mandala) ──
def mandala():
    fig,ax=newdome(); base(ax,"#140a24")
    gold=hx("#d3ac54")
    segs=[]
    for rr in np.linspace(0.10,0.96,11):
        th=np.linspace(0,2*np.pi,220); segs.append(np.column_stack([rr*np.cos(th),rr*np.sin(th)]))
    for k in range(24):
        a=2*np.pi*k/24
        segs.append(np.array([[0.06*np.cos(a),0.06*np.sin(a)],[0.96*np.cos(a),0.96*np.sin(a)]]))
    for ring_r,cnt in [(0.42,12),(0.66,18),(0.86,24)]:
        for k in range(cnt):
            a=2*np.pi*k/cnt;cu,cv=ring_r*np.cos(a),ring_r*np.sin(a)
            th=np.linspace(0,2*np.pi,64);segs.append(np.column_stack([cu+0.145*np.cos(th),cv+0.145*np.sin(th)]))
    clip(ax, ax.add_collection(LineCollection(segs,colors=[gold]*len(segs),linewidths=0.6,alpha=0.55,zorder=3)) or ax.collections[-1])
    ax.add_patch(Circle((0,0),0.05,fc=hx("#ffe6a0"),ec=hx("#caa24c"),lw=1.0,zorder=6))
    frame(ax, warm="#e8d29a", ring="#caa24c", glow=0.28, rib=False, dark=0.45)
    save(fig,"mandala")

# ── МУКАРНЫ — сталактитовый (сотовый) свод ──
def muqarnas():
    fig,ax=newdome(); base(ax,"#141018")
    tiers=[0.985,0.85,0.72,0.60,0.49,0.39,0.30,0.22,0.15,0.09]
    tile=hx("#b98d4a"); up=hx("#e6c680"); dn=hx("#4a3418")
    for ti in range(len(tiers)-1):
        r0=tiers[ti]; r1=tiers[ti+1]
        n=max(6,int(round(2*np.pi*((r0+r1)/2)/((r0-r1)*1.15))))
        off=(ti%2)*(np.pi/n)
        for kk in range(n):
            a=2*np.pi*kk/n+off; da=np.pi/n*0.96
            th=np.linspace(a-da,a+da,9)
            rr=r0-(r0-r1)*np.exp(-((th-a)/(da*0.55))**2)   # ниша: провал к центру ячейки
            us=np.concatenate([rr*np.cos(th),[r1*np.cos(a+da),r1*np.cos(a-da)]])
            vs=np.concatenate([rr*np.sin(th),[r1*np.sin(a+da),r1*np.sin(a-da)]])
            shade=0.45+0.55*(ti/len(tiers))
            col=np.clip(tile*shade+up*0.12,0,1)
            clip(ax, ax.add_collection(PolyCollection([list(zip(us,vs))],facecolors=[col],edgecolors=[dn],linewidths=0.5,zorder=3)) or ax.collections[-1])
    ax.add_patch(Circle((0,0),0.07,fc=hx("#e6c680"),ec=hx("#caa24c"),lw=1.0,zorder=6))
    frame(ax, warm="#f0d091", ring="#caa24c", glow=0.32, rib=False, dark=0.42)
    save(fig,"muqarnas")

# ── САН-МАРКО — золотой византийский свод: мозаичный фон, регистры, фигуры ──
def san_marco():
    fig,ax=newdome(); base(ax,"#3a2a0e")
    Ng=118; ii,jj=np.mgrid[0:Ng,0:Ng]; U=(jj-Ng/2+.5)/(Ng/2); V=(ii-Ng/2+.5)/(Ng/2)
    cell=2.0/Ng; gold=hx("#c9a24a"); polys=[]; cols=[]
    for x in range(Ng):
        for y in range(Ng):
            if U[x,y]**2+V[x,y]**2>0.992**2: continue
            u0,v0=U[x,y]-cell/2,V[x,y]-cell/2
            jit=(rng.random()-0.5)*0.22
            col=np.clip(gold*(1+jit)+hx("#e8cf86")*0.12*rng.random(),0,1)
            polys.append([(u0,v0),(u0+cell,v0),(u0+cell,v0+cell),(u0,v0+cell)]); cols.append(col)
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors="none",zorder=2)) or ax.collections[-1])
    for rr in (0.965,0.44):
        ax.add_patch(Circle((0,0),rr,fill=False,ec=hx("#243c78"),lw=6,zorder=3))
        ax.add_patch(Circle((0,0),rr-0.012,fill=False,ec=hx("#a5301e"),lw=1.4,zorder=3))
    th=np.linspace(0,2*np.pi,14)
    for ring_r,count,h in ((0.81,18,0.15),(0.53,12,0.14)):
        for kk in range(count):
            a=2*np.pi*kk/count+(0 if ring_r>0.7 else np.pi/count)
            d=np.array([np.cos(a),np.sin(a)]); pp=np.array([-d[1],d[0]]); ctr=ring_r*d
            foot=ctr-d*h*0.42; head=ctr+d*h*0.42
            fc=hx("#243c78") if kk%2 else hx("#7a2a1e")
            body=[tuple(foot-pp*h*0.16),tuple(head-pp*h*0.10),tuple(head+pp*h*0.10),tuple(foot+pp*h*0.16)]
            clip(ax, ax.add_collection(PolyCollection([body],facecolors=[fc],edgecolors="none",zorder=4)) or ax.collections[-1])
            hc=head+d*h*0.14
            ax.add_patch(Circle(tuple(hc),h*0.12,fc=hx("#e8cf86"),ec="none",zorder=5))
            ax.add_patch(Circle(tuple(hc),h*0.19,fill=False,ec=hx("#ffe9a8"),lw=0.7,zorder=5))
    ax.add_patch(Circle((0,0),0.17,fc=hx("#1a2a55"),ec=hx("#caa24c"),lw=2.2,zorder=6))
    ax.add_patch(Circle((0,0.02),0.055,fc=hx("#e8cf86"),ec="none",zorder=7))
    ax.add_patch(Circle((0,0.02),0.085,fill=False,ec=hx("#ffe9a8"),lw=1.1,zorder=7))
    frame(ax, warm="#ffe6a0", ring="#caa24c", glow=0.24, rib=False, dark=0.4)
    save(fig,"san_marco")

# ── ПОРТАЛ ×3 (кессонированный купол + существа), три версии ──
def _portal(tag, base_col, warm, ring, clo_h, chi_h, nbeings, bw_h, bd_h, spin):
    fig,ax=newdome(); base(ax,base_col)
    ringr=[0.985,0.86,0.73,0.60,0.47,0.35,0.24,0.15]; ribs=[36,30,24,20,16,12,8]
    clo=hx(clo_h); chi=hx(chi_h)
    for ti in range(len(ringr)-1):
        r0=ringr[ti]; r1=ringr[ti+1]; n=ribs[ti]; off=(ti%2)*(np.pi/n)
        for kk in range(n):
            a=2*np.pi*kk/n+off; da=np.pi/n*0.92; th=np.linspace(a-da,a+da,6)
            us=np.concatenate([r0*np.cos(th),r1*np.cos(th[::-1])]); vs=np.concatenate([r0*np.sin(th),r1*np.sin(th[::-1])])
            shade=0.4+0.6*(ti/len(ringr))
            clip(ax, ax.add_collection(PolyCollection([list(zip(us,vs))],facecolors=[np.clip(clo*shade+chi*0.12,0,1)],edgecolors=[chi*0.5],linewidths=0.5,zorder=3)) or ax.collections[-1])
    GA=np.pi*(3-np.sqrt(5)); th=np.linspace(0,2*np.pi,14); bw=hx(bw_h); bd=hx(bd_h)
    for i in range(1,nbeings+1):
        r=0.90*np.sqrt(i/nbeings); a=i*GA+spin; u,v=r*np.cos(a),r*np.sin(a)
        plane=i/nbeings; sz=0.026+0.026*plane; warmc=np.clip(bw*plane+bd*(1-plane),0,1)
        body=[(u+sz*0.40*np.cos(t),v+sz*0.62*np.sin(t)) for t in th]
        clip(ax, ax.add_collection(PolyCollection([body],facecolors=[warmc],edgecolors="none",zorder=6)) or ax.collections[-1])
        wl=[(u,v+sz*0.1),(u-sz*0.95,v+sz*0.55),(u-sz*0.28,v-sz*0.05)]
        wr=[(u,v+sz*0.1),(u+sz*0.95,v+sz*0.55),(u+sz*0.28,v-sz*0.05)]
        clip(ax, ax.add_collection(PolyCollection([wl,wr],facecolors=[np.clip(warmc*0.82,0,1)],edgecolors="none",zorder=6,alpha=0.9)) or ax.collections[-1])
        if plane>0.55:
            ax.add_patch(Circle((u,v+sz*0.82),sz*0.32,fill=False,ec=hx("#ffe9a8"),lw=0.7,alpha=plane,zorder=7))
    for rr,al in [(0.19,0.14),(0.13,0.22),(0.08,0.34),(0.045,0.6)]:
        ax.add_patch(Circle((0,0),rr,fc=hx(warm),ec="none",alpha=al,zorder=5))
    for _ in range(60):
        a=rng.random()*2*np.pi; r=rng.random()*0.13
        ax.add_patch(Circle((r*np.cos(a),r*np.sin(a)),0.006,fc=hx("#fff2cf"),ec="none",zorder=8))
    frame(ax, oculus=(0.0,0.0), warm=warm, ring=ring, glow=0.7, rib=False)
    save(fig,tag)

def portals():
    _portal("portal_1","#0a1430","#fff2c8","#caa24c","#22335e","#c99a3a",84,"#f2dca0","#2a3a6a",0.0)
    _portal("portal_2","#0a1230","#fff0c0","#caa24c","#26406a","#c9a84a",104,"#f2dca0","#2c3e6a",0.7)
    _portal("portal_3","#0c1226","#ffe8b0","#c9a24c","#283a64","#caa040",64,"#f4d69a","#2c3660",1.4)
    print("ok portals")

WORKS={"beam":beam,"reaction":reaction,"mandala":mandala,"muqarnas":muqarnas,"san_marco":san_marco,"portals":portals}
if __name__=="__main__":
    for a in (sys.argv[1:] or list(WORKS)): WORKS[a]()
    print("done")
