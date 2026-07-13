# -*- coding: utf-8 -*-
"""
КУПОЛА: генеративные работы как купола храмов — чистый fisheye-диск, вогнутое
затенение, свет оculus, золотой карниз. Без «железа» тарелки, без текста.
Запуск: /Users/gaidabura/cosmic-success/.venv/bin/python make_domes.py [tag...]
"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import LineCollection, PolyCollection

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(41)
VOID = "#08070e"

def hx(c):
    c = c.lstrip("#"); return np.array([int(c[i:i+2],16) for i in (0,2,4)])/255.0

def newdome():
    fig = plt.figure(figsize=(8,8), dpi=170); fig.patch.set_facecolor(VOID)
    ax = fig.add_axes([0,0,1,1]); ax.set_xlim(-1.13,1.13); ax.set_ylim(-1.13,1.13)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax

def clip(ax, art):
    art.set_clip_path(Circle((0,0),1.0, transform=ax.transData)); return art

def base(ax, col):
    ax.add_patch(Circle((0,0),1.0, fc=hx(col), ec="none", zorder=1))

def frame(ax, oculus=(0.0,0.16), warm="#f2dfae", ring="#caa24c", glow=0.55, rib=True, dark=0.62):
    N=520; xs=np.linspace(-1,1,N); xx,yy=np.meshgrid(xs,xs); r=np.hypot(xx,yy)
    ox,oy=oculus
    g=np.exp(-(((xx-ox)**2+(yy-oy)**2)/0.14))*glow
    gi=np.zeros((N,N,4)); gi[...,:3]=hx(warm); gi[...,3]=np.clip(g,0,0.7)
    clip(ax, ax.imshow(gi, extent=[-1,1,-1,1], origin="lower", zorder=30, interpolation="bilinear"))
    d=np.clip((r-0.12)/0.88,0,1)**1.9*dark
    di=np.zeros((N,N,4)); di[...,3]=d
    clip(ax, ax.imshow(di, extent=[-1,1,-1,1], origin="lower", zorder=31, interpolation="bilinear"))
    if rib:
        for rr in (0.30,0.55,0.80):
            ax.add_patch(Circle((0,0),rr, fill=False, ec=hx(ring), lw=0.5, alpha=0.14, zorder=32))
    ax.add_patch(Circle((0,0),0.998, fill=False, ec=hx(ring), lw=5.5, zorder=34))
    ax.add_patch(Circle((0,0),0.955, fill=False, ec=hx(ring), lw=1.1, alpha=0.5, zorder=34))

def save(fig, tag):
    fn=os.path.join(OUT, f"dome_{tag}.jpg")
    fig.savefig(fn, facecolor=VOID, dpi=170); plt.close(fig); print("ok", os.path.basename(fn))

# ── 1. ПЕРКОЛЬ ──
def percol():
    fig,ax=newdome(); base(ax,"#0b1226")
    N=150;p=0.5927; occ=rng.random((N,N))<p
    ii,jj=np.mgrid[0:N,0:N]; U=(jj-N/2+.5)/(N/2); V=(ii-N/2+.5)/(N/2)
    occ&=np.hypot(U,V)<0.995
    lab=np.zeros((N,N),int);cur=0
    for a in range(N):
        for b in range(N):
            if occ[a,b] and lab[a,b]==0:
                cur+=1;st=[(a,b)];lab[a,b]=cur
                while st:
                    x,y=st.pop()
                    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                        q,w=x+dx,y+dy
                        if 0<=q<N and 0<=w<N and occ[q,w] and lab[q,w]==0:
                            lab[q,w]=cur;st.append((q,w))
    sizes=np.bincount(lab.ravel());sizes[0]=0;order=np.argsort(sizes)[::-1]
    c0=hx("#1b4fa8");c1=hx("#8fb6ea");cell=2.0/N;polys=[];cols=[]
    for rank,cid in enumerate(order[:90]):
        if sizes[cid]<3:break
        t=rank/90;col=c0+(c1-c0)*t
        for x,y in zip(*np.where(lab==cid)):
            u0,v0=U[x,y]-cell/2,V[x,y]-cell/2
            polys.append([(u0,v0),(u0+cell,v0),(u0+cell,v0+cell),(u0,v0+cell)]);cols.append(col)
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=cols,linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#bcd2f2", ring="#5f86c6", glow=0.4)
    save(fig,"percol")

# ── 2. ВИТЕЛЬ ──
def vitel():
    fig,ax=newdome(); base(ax,"#160f08")
    K=8; cx=rng.uniform(-0.7,0.7,K); cy=rng.uniform(-0.7,0.7,K)
    ww=rng.uniform(0.7,1.7,K)*np.sign(rng.random(K)-0.42)
    def vel(x,y):
        u=0.0;v=0.0
        for k in range(K):
            dx=x-cx[k];dy=y-cy[k];r2=dx*dx+dy*dy+0.02
            u+=-ww[k]*dy/r2; v+=ww[k]*dx/r2
        return u,v
    GA=np.pi*(3-np.sqrt(5)); g=[];c=[];l=[]
    for m in range(360):
        r0=np.sqrt((m+.5)/360)*0.95; a0=m*GA; x,y=r0*np.cos(a0),r0*np.sin(a0); pts=[(x,y)]
        for _ in range(120):
            u,v=vel(x,y);n=np.hypot(u,v)+1e-9;x+=0.012*u/n;y+=0.012*v/n
            if x*x+y*y>0.985:break
            pts.append((x,y))
        if len(pts)<14:continue
        p=np.array(pts);key=g if rng.random()<0.6 else (c if rng.random()<0.7 else l)
        key.append((p[:,0],p[:,1]))
    for segs,col,lw,z in ((g,"#d8a93a",1.5,4),(c,"#b0321e",1.9,5),(l,"#f0dfae",0.9,6)):
        clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in segs],colors=hx(col),linewidths=lw,zorder=z,capstyle="round")) or ax.collections[-1])
    frame(ax, warm="#f4d98f", ring="#caa24c", glow=0.5)
    save(fig,"vitel")

# ── 3. ИЗМОРОЗЬ ──
def frost():
    fig,ax=newdome(); base(ax,"#0a1430")
    N=240;c=N//2;grid=np.zeros((N,N),bool);segs=[];age=[]
    for a in np.linspace(0,2*np.pi,13)[:-1]:
        i=int(c+0.97*c*np.sin(a));j=int(c+0.97*c*np.cos(a));grid[i,j]=True
    NB=((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
    placed=0;step=0
    while placed<6500 and step<1600000:
        step+=1;a=rng.random()*2*np.pi;r=np.sqrt(rng.random())*0.93*c
        i=int(c+r*np.cos(a));j=int(c+r*np.sin(a))
        for _ in range(8000):
            di,dj=NB[rng.integers(4)];i+=di;j+=dj
            if (i-c)**2+(j-c)**2>=(0.985*c)**2:
                a2=rng.random()*2*np.pi;r2=np.sqrt(rng.random())*0.93*c
                i=int(c+r2*np.cos(a2));j=int(c+r2*np.sin(a2));continue
            if grid[max(i-1,0):i+2,max(j-1,0):j+2].any():
                for d2i,d2j in NB:
                    if grid[i+d2i,j+d2j]:
                        segs.append(((j-c)/c,(i-c)/c,(j+d2j-c)/c,(i+d2i-c)/c));break
                grid[i,j]=True;age.append(placed);placed+=1;break
    t=np.array(age)/max(placed,1);buck=np.digitize(t,[0.25,0.5,0.75])
    pal=["#f2f6fc","#d7e2f2","#b4c8e8","#8fabdb"];lws=[2.4,1.7,1.2,0.8]
    for b in range(4):
        ss=[(np.array([x1,x2]),np.array([y1,y2])) for (x1,y1,x2,y2),bb in zip(segs,buck) if bb==b]
        if ss: clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx(pal[b]),linewidths=lws[b],zorder=4+b,capstyle="round")) or ax.collections[-1])
    frame(ax, warm="#cfe0f5", ring="#7f9fc6", glow=0.32, rib=False)
    save(fig,"frost")

# ── 4. ГРОЗА ──
def groza():
    fig,ax=newdome(); base(ax,"#0d0a12")
    N=240;c=N//2;grid=np.zeros((N,N),bool);depth=np.zeros((N,N),int)
    grid[int(c-0.90*c),c]=True;segs=[];sdep=[]
    NB=((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1));hits=np.zeros((N,N),np.int8)
    placed=0;step=0
    while placed<7500 and step<7000000:
        step+=1;a=rng.random()*2*np.pi;r=np.sqrt(rng.random())*0.9*c
        i=int(c+r*np.cos(a));j=int(c+r*np.sin(a))
        for _ in range(9000):
            u=rng.random()
            di,dj=(-1,0) if u<0.34 else (1,0) if u<0.5 else (0,1) if u<0.75 else (0,-1)
            i+=di;j+=dj
            if (i-c)**2+(j-c)**2>=(0.965*c)**2:
                a2=rng.random()*2*np.pi;r2=np.sqrt(rng.random())*0.9*c
                i=int(c+r2*np.cos(a2));j=int(c+r2*np.sin(a2));continue
            if grid[max(i-1,0):i+2,max(j-1,0):j+2].any():
                hits[i,j]+=1
                if hits[i,j]<3:break
                best=None
                for d2i,d2j in NB:
                    if grid[i+d2i,j+d2j] and (best is None or depth[i+d2i,j+d2j]<best[2]):
                        best=(i+d2i,j+d2j,depth[i+d2i,j+d2j])
                grid[i,j]=True;depth[i,j]=best[2]+1
                segs.append(((j-c)/c,(i-c)/c,(best[1]-c)/c,(best[0]-c)/c));sdep.append(best[2]+1);placed+=1;break
    t=np.array(sdep)/max(sdep);buck=np.digitize(t,[0.2,0.45,0.7])
    char=["#140b05","#201307","#2e1c0a","#3e260e"];glw=[5.6,3.9,2.7,1.7]
    for b in range(4):
        ss=[(np.array([x1,x2]),np.array([y1,y2])) for (x1,y1,x2,y2),bb in zip(segs,buck) if bb==b]
        if not ss:continue
        clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx(char[b]),linewidths=glw[b],zorder=4)) or ax.collections[-1])
        clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx("#edc25a"),linewidths=glw[b]*0.40,zorder=5)) or ax.collections[-1])
    frame(ax, oculus=(0.0,-0.62), warm="#f1cf7a", ring="#caa24c", glow=0.42, rib=False, dark=0.40)
    save(fig,"groza")

# ── 5. МАЯТНИК ──
def mayatnik():
    fig,ax=newdome(); base(ax,"#0c0b0f")
    def deriv(s):
        g=9.81;t1,t2,w1,w2=s;d=t1-t2;cd,sd=np.cos(d),np.sin(d);den=2-cd*cd
        a1=(-w1*w1*sd*cd-w2*w2*sd-2*g*np.sin(t1)+g*np.sin(t2)*cd)/den
        a2=(2*(w1*w1*sd+g*np.sin(t1)*cd-g*np.sin(t2))+w2*w2*sd*cd)/den
        return np.array([w1,w2,a1,a2])
    pal=["#f4d98a","#e0b452","#c99a3a","#a8791f","#e8c46a"]
    for tr,eps in enumerate((0.0,8e-4,1.6e-3,2.4e-3,3.2e-3)):
        s=np.array([2.3+eps,2.7,0.0,0.0]);pts=[];dt=0.005
        for _ in range(8200):
            k1=deriv(s);k2=deriv(s+dt/2*k1);k3=deriv(s+dt/2*k2);k4=deriv(s+dt*k3)
            s=s+dt/6*(k1+2*k2+2*k3+k4)
            x=np.sin(s[0])+np.sin(s[1]);y=-np.cos(s[0])-np.cos(s[1])
            pts.append((x*0.34,y*0.34+0.04))
        p=np.array(pts);keep=p[:,0]**2+p[:,1]**2<0.94;run=[]
        for i in range(len(p)):
            if keep[i]:run.append(p[i])
            elif len(run)>12:
                q=np.array(run)
                clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=3.4,zorder=3,alpha=0.10)) or ax.collections[-1])
                clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=1.15,zorder=4+tr,alpha=0.9)) or ax.collections[-1])
                run=[]
            else:run=[]
        if len(run)>12:
            q=np.array(run)
            clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=3.4,zorder=3,alpha=0.10)) or ax.collections[-1])
            clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=1.15,zorder=4+tr,alpha=0.9)) or ax.collections[-1])
    frame(ax, warm="#f0d692", ring="#caa24c", glow=0.30, rib=False, dark=0.34)
    save(fig,"mayatnik")

# ── 6. ОСЫПЬ (абелева куча — центрированная мандала) ──
def osyp():
    fig,ax=newdome(); base(ax,"#1a0f0a")
    N=241;Z=np.zeros((N,N),int);c=N//2;Z[c,c]=45000
    while (Z>=4).any():
        t=(Z>=4);Z[t]-=4
        Z[1:,:]+=t[:-1,:];Z[:-1,:]+=t[1:,:];Z[:,1:]+=t[:,:-1];Z[:,:-1]+=t[:,1:]
    ii,jj=np.mgrid[0:N,0:N];U=(jj-c)/c;V=(ii-c)/c;mask=np.hypot(U,V)<0.995
    pal=[hx("#1a0f0a"),hx("#7a3b22"),hx("#c9803e"),hx("#f0d3a0")];cell=2.0/N;polys=[];cols=[]
    for h in (1,2,3):
        for x,y in zip(*np.where((Z==h)&mask)):
            u0,v0=U[x,y]-cell/2,V[x,y]-cell/2
            polys.append([(u0,v0),(u0+cell,v0),(u0+cell,v0+cell),(u0,v0+cell)]);cols.append(pal[h])
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=cols,linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#f3d59f", ring="#caa24c", glow=0.34, rib=False, dark=0.5)
    save(fig,"osyp")

# ── 7. НАБОР (Rule 30 по кольцам) ──
def nabor():
    fig,ax=newdome(); base(ax,"#efe6d2")
    K=240;ROWS=48;state=np.zeros(K,bool);state[np.arange(0,K,K//12)]=True
    red=hx("#a5301e");dark=hx("#5f1c10");polys=[];cols=[];r_out=0.97
    for row in range(ROWS):
        r1=r_out*(1-row/ROWS)**0.82;r0=r_out*(1-(row+0.82)/ROWS)**0.82
        if r0<0.05:break
        for k in range(K):
            if not state[k]:continue
            a0=2*np.pi*k/K;a1=2*np.pi*(k+0.82)/K;th=np.linspace(a0,a1,5)
            us=np.concatenate([r1*np.cos(th),r0*np.cos(th[::-1])]);vs=np.concatenate([r1*np.sin(th),r0*np.sin(th[::-1])])
            polys.append(list(zip(us,vs)));cols.append(red if (row+k)%7 else dark)
        L=np.roll(state,1);R=np.roll(state,-1);state=np.logical_xor(L,np.logical_or(state,R))
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=cols,linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#8a2a1a", ring="#7a2417", glow=0.16, rib=False)
    save(fig,"nabor")

# ── 8. ЧЕРНЬ-ДОМЕН (Изинг при T_c) ──
def chern():
    fig,ax=newdome(); base(ax,"#cbcdd4")
    N=200;S=rng.choice(np.array([-1,1],np.int8),(N,N));beta=1/2.269;idx=np.indices((N,N)).sum(0)%2
    for _ in range(80):
        for par in (0,1):
            nb=np.roll(S,1,0)+np.roll(S,-1,0)+np.roll(S,1,1)+np.roll(S,-1,1)
            dE=2*S*nb;acc=(dE<=0)|(rng.random((N,N))<np.exp(-beta*np.clip(dE,0,40)))
            S[acc&(idx==par)]*=-1
    ii,jj=np.mgrid[0:N,0:N];U=(jj-N/2+.5)/(N/2);V=(ii-N/2+.5)/(N/2);mask=np.hypot(U,V)<0.995
    cell=2.0/N;niello=hx("#14161c");polys=[]
    for x,y in zip(*np.where((S<0)&mask)):
        u0,v0=U[x,y]-cell/2,V[x,y]-cell/2
        polys.append([(u0,v0),(u0+cell,v0),(u0+cell,v0+cell),(u0,v0+cell)])
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=[niello]*len(polys),edgecolors=[niello]*len(polys),linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#e8eaef", ring="#8f929c", glow=0.22, rib=False)
    save(fig,"chern")

# ── 9. ПОРТАЛ (кессонированный купол + существа) ──
def portal():
    fig,ax=newdome(); base(ax,"#0a1024")
    # кессоны: концентрические кольца + радиальные рёбра, сжимаются к оculus
    ringr=[0.985,0.86,0.73,0.60,0.47,0.35,0.24,0.15]
    ribs=[36,30,24,20,16,12,8]
    bronze=hx("#6a5626");gold=hx("#c99a3a")
    for ti in range(len(ringr)-1):
        r0=ringr[ti];r1=ringr[ti+1];n=ribs[ti];off=(ti%2)*(np.pi/n)
        for k in range(n):
            a=2*np.pi*k/n+off;da=np.pi/n*0.92
            th=np.linspace(a-da,a+da,6)
            us=np.concatenate([r0*np.cos(th),r1*np.cos(th[::-1])]);vs=np.concatenate([r0*np.sin(th),r1*np.sin(th[::-1])])
            shade=0.4+0.6*(ti/len(ringr))
            clip(ax, ax.add_collection(PolyCollection([list(zip(us,vs))],facecolors=[bronze*shade+gold*0.12],edgecolors=[gold*0.5],linewidths=0.5,zorder=3)) or ax.collections[-1])
    # существа по золотой спирали
    GA=np.pi*(3-np.sqrt(5));th=np.linspace(0,2*np.pi,16)
    for i in range(1,64):
        r=0.9*np.sqrt(i/64);a=i*GA;u,v=r*np.cos(a),r*np.sin(a)
        plane=i/64;sz=0.045*(0.5+plane)
        warm=np.clip(hx("#f0dca0")*plane+hx("#3a3050")*(1-plane),0,1)
        # тело-капля
        clip(ax, ax.add_collection(PolyCollection([[(u+sz*np.cos(t)*0.5,v+sz*np.sin(t)) for t in th]],facecolors=[warm],edgecolors="none",zorder=6)) or ax.collections[-1])
        # нимб
        if plane>0.5:
            ax.add_patch(Circle((u,v+sz*0.9),sz*0.5,fill=False,ec=hx("#ffe9a8"),lw=0.6,alpha=plane,zorder=7))
    # искры у оculus
    for _ in range(60):
        a=rng.random()*2*np.pi;r=rng.random()*0.14
        ax.add_patch(Circle((r*np.cos(a),r*np.sin(a)+0.0),0.006,fc=hx("#fff2cf"),ec="none",zorder=8))
    frame(ax, oculus=(0.0,0.0), warm="#ffe9a8", ring="#caa24c", glow=0.7, rib=False)
    save(fig,"portal")

# ── 10. ФИЛЛОТАКСИС (золотой купол зёрен) ──
def phyllo():
    fig,ax=newdome(); base(ax,"#0e0b18")
    N=1400;GA=np.pi*(3-np.sqrt(5));th=np.linspace(0,2*np.pi,14);polys=[];cols=[]
    for i in range(N):
        r=np.sqrt(i/N)*0.97;a=i*GA;u,v=r*np.cos(a),r*np.sin(a)
        if u*u+v*v>0.985:continue
        sz=0.008+0.018*(i/N)
        warm=np.clip(hx("#c98a2a")*(0.5+0.6*(i/N))+hx("#f0d48a")*(1-i/N)*0.5,0,1)
        polys.append([(u+sz*np.cos(t),v+sz*np.sin(t)) for t in th]);cols.append(warm)
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=hx("#0e0b18"),linewidths=0.15,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#f4d98f", ring="#caa24c", glow=0.42, rib=False)
    save(fig,"phyllo")

WORKS={"percol":percol,"vitel":vitel,"frost":frost,"groza":groza,"mayatnik":mayatnik,
       "osyp":osyp,"nabor":nabor,"chern":chern,"portal":portal,"phyllo":phyllo}
if __name__=="__main__":
    for a in (sys.argv[1:] or list(WORKS)): WORKS[a]()
    print("done")
