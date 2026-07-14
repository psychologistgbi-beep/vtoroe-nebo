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

def frame(ax, oculus=(0.0,0.16), warm="#f2dfae", ring="#caa24c", glow=0.55, rib=True, dark=0.62, planet=True):
    # ПЛАНЕТА (planet=True): выпуклый шар-мир в космосе — прозрачный фон (звёзды на
    # странице, общий космос под всеми планетами), глубокий терминатор, блик, атмосферный
    # лимб. Симметрично, строго фронтально. planet=False → купол-окулюс (для hero).
    W=1.13; N=560; xs=np.linspace(-W,W,N); xx,yy=np.meshgrid(xs,xs); r=np.hypot(xx,yy)
    inside=r<=1.0
    z=np.sqrt(np.clip(1-np.clip(r,0,1)**2,0,1))
    Lx,Ly,Lz=-0.42,0.52,0.74; ln=(Lx*Lx+Ly*Ly+Lz*Lz)**0.5; Lx,Ly,Lz=Lx/ln,Ly/ln,Lz/ln
    ndotl=np.clip(xx*Lx+yy*Ly+z*Lz,0,1)
    shade=0.38+0.62*ndotl
    dA=np.where(inside, np.clip((1-shade)**1.15*(0.6+dark*0.55),0,0.92), 0.0)   # глубже терминатор
    di=np.zeros((N,N,4)); di[...,3]=dA
    ax.imshow(di, extent=[-W,W,-W,W], origin="lower", zorder=30, interpolation="bilinear")
    if planet:
        # блик (спекуляр) у подсолнечной точки
        spx,spy=Lx*0.86,Ly*0.86; sig=0.22
        sp=np.where(inside, np.exp(-(((xx-spx)**2+(yy-spy)**2)/(2*sig*sig)))*0.34, 0.0)
        spi=np.zeros((N,N,4)); spi[...,:3]=hx(warm); spi[...,3]=sp
        ax.imshow(spi, extent=[-W,W,-W,W], origin="lower", zorder=31, interpolation="bilinear")
        # атмосферный лимб (тонкое свечение по краю, ярче на свету) — за пределы диска
        atmo=np.exp(-((r-1.0)/0.05)**2)*(0.25+0.75*ndotl)
        atm=np.zeros((N,N,4)); atm[...,:3]=hx("#bcd0f0"); atm[...,3]=np.clip(atmo*0.6,0,0.6)
        ax.imshow(atm, extent=[-W,W,-W,W], origin="lower", zorder=33, interpolation="bilinear")
    else:
        hiA=np.where(inside, np.clip((shade-0.80)*2.4,0,0.32), 0.0)
        hii=np.zeros((N,N,4)); hii[...,:3]=hx(warm); hii[...,3]=hiA
        ax.imshow(hii, extent=[-W,W,-W,W], origin="lower", zorder=31, interpolation="bilinear")
        if glow>0:
            ox,oy=oculus; g=np.exp(-(((xx-ox)**2+(yy-oy)**2)/0.11))*min(glow,0.5)
            gi=np.zeros((N,N,4)); gi[...,:3]=hx(warm); gi[...,3]=np.clip(g,0,0.5)
            clip(ax, ax.imshow(gi, extent=[-W,W,-W,W], origin="lower", zorder=32, interpolation="bilinear"))
        ax.add_patch(Circle((0,0),0.997, fill=False, ec=hx(ring), lw=1.4, alpha=0.4, zorder=34))

def save(fig, tag):
    fn=os.path.join(OUT, f"dome_{tag}.png")
    fig.savefig(fn, transparent=True, dpi=170); plt.close(fig); print("ok", os.path.basename(fn))

# ── 1. ПЕРКОЛЬ ──
def percol():
    fig,ax=newdome(); base(ax,"#e6ecf6")
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
    c0=hx("#123c8c");c1=hx("#5f86c6");cell=2.0/N;polys=[];cols=[]
    for rank,cid in enumerate(order[:90]):
        if sizes[cid]<3:break
        t=rank/90;col=c0+(c1-c0)*t
        for x,y in zip(*np.where(lab==cid)):
            u0,v0=U[x,y]-cell/2,V[x,y]-cell/2
            polys.append([(u0,v0),(u0+cell,v0),(u0+cell,v0+cell),(u0,v0+cell)]);cols.append(col)
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=cols,linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#dfeafa", ring="#5f86c6", glow=0.0, dark=0.5)
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
    N=260;c=N//2;grid=np.zeros((N,N),bool);segs=[];age=[]
    for a in np.linspace(0,2*np.pi,80,endpoint=False):
        i=int(c+0.985*c*np.sin(a));j=int(c+0.985*c*np.cos(a));grid[i,j]=True
    NB=((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
    placed=0;step=0
    while placed<13000 and step<9000000:
        step+=1;a=rng.random()*2*np.pi;r=(0.28+0.70*rng.random())*c
        i=int(c+r*np.cos(a));j=int(c+r*np.sin(a))
        for _ in range(6000):
            di,dj=NB[rng.integers(8)];i+=di;j+=dj
            if i<1 or j<1 or i>=N-1 or j>=N-1 or (i-c)**2+(j-c)**2>=(0.992*c)**2:
                a=rng.random()*2*np.pi;r=(0.28+0.70*rng.random())*c
                i=int(c+r*np.cos(a));j=int(c+r*np.sin(a));continue
            if grid[i-1:i+2,j-1:j+2].any():
                for d2i,d2j in NB:
                    if grid[i+d2i,j+d2j]:
                        segs.append(((j-c)/c,(i-c)/c,(j+d2j-c)/c,(i+d2i-c)/c));break
                grid[i,j]=True;age.append(placed);placed+=1;break
    t=np.array(age)/max(placed,1);buck=np.digitize(t,[0.25,0.5,0.75])
    pal=["#f2f6fc","#d7e2f2","#b4c8e8","#8fabdb"];lws=[1.9,1.5,1.1,0.8]
    for b in range(4):
        ss=[(np.array([x1,x2]),np.array([y1,y2])) for (x1,y1,x2,y2),bb in zip(segs,buck) if bb==b]
        if ss: clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx(pal[b]),linewidths=lws[b],zorder=4+b,capstyle="round")) or ax.collections[-1])
    frame(ax, warm="#cfe0f5", ring="#7f9fc6", glow=0.30, rib=False, dark=0.5)
    save(fig,"frost")

# ── 4. ГРОЗА ──
def groza():
    fig,ax=newdome(); base(ax,"#0d0a12")
    N=260;c=N//2;grid=np.zeros((N,N),bool);depth=np.zeros((N,N),int)
    grid[c,c]=True;segs=[];sdep=[];maxr=1.0;RIM=0.992*c
    NB=((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
    placed=0;step=0
    while placed<12000 and step<12000000:
        step+=1
        birth=min(maxr+9,RIM);kill2=min(maxr+26,RIM+6)**2
        a=rng.random()*2*np.pi;i=int(c+birth*np.cos(a));j=int(c+birth*np.sin(a))
        for _ in range(5000):
            di,dj=NB[rng.integers(4)];i+=di;j+=dj
            rr2=(i-c)**2+(j-c)**2
            if i<1 or j<1 or i>=N-1 or j>=N-1 or rr2>kill2:
                a=rng.random()*2*np.pi;i=int(c+birth*np.cos(a));j=int(c+birth*np.sin(a));continue
            if grid[i-1:i+2,j-1:j+2].any():
                best=None
                for d2i,d2j in NB:
                    if grid[i+d2i,j+d2j] and (best is None or depth[i+d2i,j+d2j]<best[2]):
                        best=(i+d2i,j+d2j,depth[i+d2i,j+d2j])
                grid[i,j]=True;depth[i,j]=best[2]+1;maxr=max(maxr,rr2**0.5)
                segs.append(((j-c)/c,(i-c)/c,(best[1]-c)/c,(best[0]-c)/c));sdep.append(best[2]+1);placed+=1;break
    t=np.array(sdep)/max(sdep);buck=np.digitize(t,[0.25,0.5,0.75])
    char=["#140b05","#201307","#2e1c0a","#3e260e"];glw=[4.2,3.0,2.1,1.4]
    for b in range(4):
        ss=[(np.array([x1,x2]),np.array([y1,y2])) for (x1,y1,x2,y2),bb in zip(segs,buck) if bb==b]
        if not ss:continue
        clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx(char[b]),linewidths=glw[b],zorder=4)) or ax.collections[-1])
        clip(ax, ax.add_collection(LineCollection([np.column_stack(s) for s in ss],colors=hx("#edc25a"),linewidths=glw[b]*0.42,zorder=5)) or ax.collections[-1])
    frame(ax, oculus=(0.0,0.0), warm="#f1cf7a", ring="#caa24c", glow=0.5, rib=False, dark=0.42)
    save(fig,"groza")

# ── 5. МАЯТНИК ──
def mayatnik():
    fig,ax=newdome(); base(ax,"#0c0b0f")
    def deriv(s):
        g=9.81;t1,t2,w1,w2=s;d=t1-t2;cd,sd=np.cos(d),np.sin(d);den=2-cd*cd
        a1=(-w1*w1*sd*cd-w2*w2*sd-2*g*np.sin(t1)+g*np.sin(t2)*cd)/den
        a2=(2*(w1*w1*sd+g*np.sin(t1)*cd-g*np.sin(t2))+w2*w2*sd*cd)/den
        return np.array([w1,w2,a1,a2])
    pal=["#f4d98a","#e0b452","#c99a3a","#a8791f","#e8c46a","#d8b45a","#c9a24a","#f0d090"]
    inits=[(2.30,2.70),(2.50,2.35),(2.05,2.90),(2.70,2.15),(2.15,2.55),(2.60,2.82),(2.42,2.05),(2.20,3.00)]
    def flush(run,tr):
        if len(run)>10:
            q=np.array(run)
            clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=3.0,zorder=3,alpha=0.09)) or ax.collections[-1])
            clip(ax, ax.add_collection(LineCollection([q],colors=hx(pal[tr]),linewidths=1.0,zorder=4+tr,alpha=0.82)) or ax.collections[-1])
    for tr,(A0,B0) in enumerate(inits):
        s=np.array([A0,B0,0.0,0.0]);pts=[];dt=0.005
        for _ in range(7400):
            k1=deriv(s);k2=deriv(s+dt/2*k1);k3=deriv(s+dt/2*k2);k4=deriv(s+dt*k3)
            s=s+dt/6*(k1+2*k2+2*k3+k4)
            x=np.sin(s[0])+np.sin(s[1]);y=-np.cos(s[0])-np.cos(s[1])
            pts.append((x*0.46,y*0.46+0.02))
        p=np.array(pts);keep=p[:,0]**2+p[:,1]**2<0.955;run=[]
        for i in range(len(p)):
            if keep[i]:run.append(p[i])
            else:flush(run,tr);run=[]
        flush(run,tr)
    frame(ax, warm="#f0d692", ring="#caa24c", glow=0.30, rib=False, dark=0.34)
    save(fig,"mayatnik")

# ── 6. ОСЫПЬ (абелева куча — центрированная мандала, заполняет круг) ──
def osyp():
    fig,ax=newdome(); base(ax,"#1a0f0a")
    N=351;Z=np.zeros((N,N),int);c=N//2;Z[c,c]=150000
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
    frame(ax, warm="#f3d59f", ring="#caa24c", glow=0.30, rib=False, dark=0.5)
    save(fig,"osyp")

# ── 7. НАБОР (Rule 30 по кольцам, розетка на тёмном) ──
def nabor():
    fig,ax=newdome(); base(ax,"#170a09")
    K=240;ROWS=52;state=np.zeros(K,bool);state[np.arange(0,K,K//12)]=True
    red=hx("#c23a24");gold=hx("#e0a848");polys=[];cols=[];r_out=0.99
    for row in range(ROWS):
        r1=r_out*(1-row/ROWS)**0.80;r0=r_out*(1-(row+0.82)/ROWS)**0.80
        if r0<0.03:break
        for k in range(K):
            if not state[k]:continue
            a0=2*np.pi*k/K;a1=2*np.pi*(k+0.82)/K;th=np.linspace(a0,a1,5)
            us=np.concatenate([r1*np.cos(th),r0*np.cos(th[::-1])]);vs=np.concatenate([r1*np.sin(th),r0*np.sin(th[::-1])])
            polys.append(list(zip(us,vs)));cols.append(red if (row+k)%6 else gold)
        L=np.roll(state,1);R=np.roll(state,-1);state=np.logical_xor(L,np.logical_or(state,R))
    clip(ax, ax.add_collection(PolyCollection(polys,facecolors=cols,edgecolors=cols,linewidths=0.1,zorder=3)) or ax.collections[-1])
    frame(ax, warm="#e5b26a", ring="#b06a2a", glow=0.26, rib=False, dark=0.5)
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
    # существа по золотой спирали — капля с крыльями
    GA=np.pi*(3-np.sqrt(5));th=np.linspace(0,2*np.pi,14)
    for i in range(1,84):
        r=0.90*np.sqrt(i/84);a=i*GA;u,v=r*np.cos(a),r*np.sin(a)
        plane=i/84;sz=0.026+0.026*plane
        warm=np.clip(hx("#f2dca0")*plane+hx("#5a4a68")*(1-plane),0,1)
        body=[(u+sz*0.40*np.cos(t),v+sz*0.62*np.sin(t)) for t in th]
        clip(ax, ax.add_collection(PolyCollection([body],facecolors=[warm],edgecolors="none",zorder=6)) or ax.collections[-1])
        wl=[(u,v+sz*0.1),(u-sz*0.95,v+sz*0.55),(u-sz*0.28,v-sz*0.05)]
        wr=[(u,v+sz*0.1),(u+sz*0.95,v+sz*0.55),(u+sz*0.28,v-sz*0.05)]
        clip(ax, ax.add_collection(PolyCollection([wl,wr],facecolors=[np.clip(warm*0.82,0,1)],edgecolors="none",zorder=6,alpha=0.9)) or ax.collections[-1])
        if plane>0.55:
            ax.add_patch(Circle((u,v+sz*0.82),sz*0.32,fill=False,ec=hx("#ffe9a8"),lw=0.7,alpha=plane,zorder=7))
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
    frame(ax, warm="#f4d98f", ring="#caa24c", glow=0.42, rib=False, planet=False)  # hero — купол-окулюс
    save(fig,"phyllo")

WORKS={"percol":percol,"vitel":vitel,"frost":frost,"groza":groza,"mayatnik":mayatnik,
       "osyp":osyp,"nabor":nabor,"chern":chern,"portal":portal,"phyllo":phyllo}
if __name__=="__main__":
    for a in (sys.argv[1:] or list(WORKS)): WORKS[a]()
    print("done")
