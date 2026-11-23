import json,os,sys,random,urllib.request,urllib.error

U=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
V=[0,100,320,330,500,900,0]
# Piece-square tables from White's side, a8 first: pawn, knight, bishop,
# rook, queen, king middlegame, king endgame.
PT=[
[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],
[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
[-50,-40,-30,-20,-20,-30,-40,-50,-30,-20,-10,0,0,-10,-20,-30,-30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,-30,-30,0,0,0,0,-30,-30,-50,-30,-30,-30,-30,-30,-30,-50],
]
random.seed(11235813)
Z=[[random.getrandbits(64) for _ in range(64)] for _ in range(13)]
ZS=random.getrandbits(64)
ZC=[random.getrandbits(64) for _ in range(16)]
ZE=[random.getrandbits(64) for _ in range(8)]
KN=[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
KG=[(dr,df) for dr in(-1,0,1) for df in(-1,0,1) if dr or df]
DG=[(-1,-1),(-1,1),(1,-1),(1,1)]
ST=[(-1,0),(1,0),(0,-1),(0,1)]
CMR={63:1,56:2,7:4,0:8}
MATE=100000
INF=10**9
BUDGET=72000
B=[0]*64
TURN=1
CAST=0
EP=-1
KEY=0
PHASE=24
KP={1:60,-1:4}
TT={}
KILL=[[None,None] for _ in range(128)]
HIST={}
GKEYS=set()
NODES=0

class TO(Exception):pass

def att(sq,by):
    f=sq&7;r=sq>>3
    if by>0:
        if f<7 and sq+9<64 and B[sq+9]==1:return True
        if f>0 and sq+7<64 and B[sq+7]==1:return True
    else:
        if f<7 and sq-7>=0 and B[sq-7]==-1:return True
        if f>0 and sq-9>=0 and B[sq-9]==-1:return True
    for dr,df in KN:
        nf,nr=f+df,r+dr
        if 0<=nf<8 and 0<=nr<8 and B[nr*8+nf]==2*by:return True
    for dr,df in KG:
        nf,nr=f+df,r+dr
        if 0<=nf<8 and 0<=nr<8 and B[nr*8+nf]==6*by:return True
    for dirs,ks in((DG,(3,5)),(ST,(4,5))):
        for dr,df in dirs:
            nf,nr=f+df,r+dr
            while 0<=nf<8 and 0<=nr<8:
                p=B[nr*8+nf]
                if p:
                    if (p>0)==(by>0) and abs(p) in ks:return True
                    break
                nf+=df;nr+=dr
    return False

def moves(cap=False):
    res=[]
    me=TURN>0
    for s in range(64):
        p=B[s]
        if not p or (p>0)!=me:continue
        a=abs(p);f=s&7;r=s>>3
        if a==1:
            d=-8 if me else 8
            start=6 if me else 1
            last=0 if me else 7
            t=s+d
            if not B[t] and (not cap or (t>>3)==last):
                if (t>>3)==last:
                    for pr in(5,4,3,2):res.append((s,t,pr))
                elif not cap:
                    res.append((s,t,0))
                    if r==start and not B[s+2*d]:res.append((s,s+2*d,0))
            for df in(-1,1):
                nf=f+df
                if 0<=nf<8:
                    t=s+d+df
                    q=B[t]
                    if q and (q>0)!=me:
                        if (t>>3)==last:
                            for pr in(5,4,3,2):res.append((s,t,pr))
                        else:res.append((s,t,0))
                    elif t==EP:res.append((s,t,0))
        elif a==2 or a==6:
            for dr,df in(KN if a==2 else KG):
                nf,nr=f+df,r+dr
                if 0<=nf<8 and 0<=nr<8:
                    t=nr*8+nf;q=B[t]
                    if not q:
                        if not cap:res.append((s,t,0))
                    elif (q>0)!=me:res.append((s,t,0))
        else:
            for dr,df in(DG if a==3 else ST if a==4 else DG+ST):
                nf,nr=f+df,r+dr
                while 0<=nf<8 and 0<=nr<8:
                    t=nr*8+nf;q=B[t]
                    if q:
                        if (q>0)!=me:res.append((s,t,0))
                        break
                    if not cap:res.append((s,t,0))
                    nf+=df;nr+=dr
        if a==6 and not cap:
            if me and s==60:
                if CAST&1 and not B[61] and not B[62] and B[63]==4 and not att(60,-1) and not att(61,-1) and not att(62,-1):res.append((60,62,0))
                if CAST&2 and not B[59] and not B[58] and not B[57] and B[56]==4 and not att(60,-1) and not att(59,-1) and not att(58,-1):res.append((60,58,0))
            if not me and s==4:
                if CAST&4 and not B[5] and not B[6] and B[7]==-4 and not att(4,1) and not att(5,1) and not att(6,1):res.append((4,6,0))
                if CAST&8 and not B[3] and not B[2] and not B[1] and B[0]==-4 and not att(4,1) and not att(3,1) and not att(2,1):res.append((4,2,0))
    return res

def pw(cap):
    a=abs(cap)
    return 1 if a in(2,3) else 2 if a==4 else 4 if a==5 else 0

def make(m):
    global TURN,CAST,EP,KEY,PHASE
    s,t,pr=m
    p=B[s];cap=B[t];cs=-1
    old=(KEY,EP,CAST)
    KEY^=ZC[CAST]
    if EP>=0:KEY^=ZE[EP&7]
    EP=-1
    if cap:
        KEY^=Z[cap+6][t]
        PHASE-=pw(cap)
        if abs(cap)==4:CAST&=~CMR.get(t,0)
    B[t]=p;B[s]=0
    KEY^=Z[p+6][s]^Z[p+6][t]
    if pr:
        B[t]=pr*TURN
        KEY^=Z[p+6][t]^Z[pr*TURN+6][t]
    if abs(p)==1:
        if t==old[1] and not cap and (s&7)!=(t&7):
            cs=t+8 if TURN>0 else t-8
            KEY^=Z[-TURN+6][cs]
            cap=B[cs];B[cs]=0
        elif abs(t-s)==16:
            EP=(s+t)//2
            KEY^=ZE[EP&7]
    if abs(p)==6:
        KP[TURN]=t
        CAST&=~(3 if TURN>0 else 12)
        if abs(t-s)==2:
            if TURN>0:rf,rt=(63,61) if t>s else (56,59)
            else:rf,rt=(7,5) if t>s else (0,3)
            B[rt]=B[rf];B[rf]=0
            KEY^=Z[4*TURN+6][rf]^Z[4*TURN+6][rt]
    if abs(p)==4:CAST&=~CMR.get(s,0)
    KEY^=ZC[CAST]^ZS
    TURN=-TURN
    return (m,cap,cs,old)

def unmake(u):
    global TURN,CAST,EP,KEY,PHASE
    m,cap,cs,old=u
    KEY,EP,CAST=old
    TURN=-TURN
    s,t,pr=m
    p=B[t]
    if pr:p=TURN
    B[s]=p;B[t]=0
    if cap:
        PHASE+=pw(cap)
        if cs>=0:B[cs]=cap
        else:B[t]=cap
    if abs(p)==6:
        KP[TURN]=s
        if abs(t-s)==2:
            if TURN>0:rf,rt=(63,61) if t>s else (56,59)
            else:rf,rt=(7,5) if t>s else (0,3)
            B[rf]=B[rt];B[rt]=0

def evaluate():
    sc=0
    pf={1:[0]*8,-1:[0]*8}
    bp={1:0,-1:0}
    rf={1:[],-1:[]}
    for s in range(64):
        p=B[s]
        if not p:continue
        a=abs(p)
        col=1 if p>0 else -1
        if a==1:pf[col][s&7]+=1
        elif a==3:bp[col]+=1
        elif a==4:rf[col].append(s&7)
        if a==6:
            ss=s if col>0 else s^56
            sc+=col*((PT[5][ss]*PHASE+PT[6][ss]*(24-PHASE))//24)
            continue
        tab=PT[a-1]
        sc+=col*(V[a]+(tab[s] if col>0 else tab[s^56]))
    for col in(1,-1):
        if bp[col]>=2:sc+=col*25
        c=pf[col]
        for f in range(8):
            if c[f]>1:sc-=col*12*(c[f]-1)
            if c[f] and (f==0 or not c[f-1]) and (f==7 or not c[f+1]):sc-=col*10
        for f in rf[col]:
            if not pf[-col][f]:sc+=col*(15 if not c[f] else 8)
    return sc

def order(ms,ttm,ply):
    def k(m):
        if m==ttm:return 10**7
        s,t,pr=m
        v=B[t]
        if not v and EP>=0 and t==EP and abs(B[s])==1 and (s&7)!=(t&7):v=-TURN
        if v:return 100000+V[abs(v)]*16-abs(B[s])+(V[pr] if pr else 0)
        if pr:return 95000+V[pr]
        kk=KILL[ply]
        if m==kk[0]:return 90000
        if m==kk[1]:return 80000
        return HIST.get((TURN,s,t),0)
    return sorted(ms,key=k,reverse=True)

def qsearch(alpha,beta,ply):
    global NODES
    NODES+=1
    if NODES>=BUDGET:raise TO
    if KEY in GKEYS:return 0
    if ply>=64:return TURN*evaluate()
    inchk=att(KP[TURN],-TURN)
    if inchk:
        best=-INF
    else:
        best=TURN*evaluate()
        if best>=beta:return beta
        if best>alpha:alpha=best
    legal=0
    for m in order(moves(not inchk),None,ply):
        if not inchk and not m[2] and B[m[1]] and best+V[abs(B[m[1]])]+200<alpha:continue
        u=make(m)
        if att(KP[-TURN],TURN):
            unmake(u);continue
        legal+=1
        sc=-qsearch(-beta,-alpha,ply+1)
        unmake(u)
        if sc>best:best=sc
        if sc>alpha:alpha=sc
        if alpha>=beta:break
    if inchk and not legal:return -MATE+ply
    return best

def search(depth,alpha,beta,ply):
    global NODES
    if ply>0 and KEY in GKEYS:return 0
    if depth<=0:return qsearch(alpha,beta,ply)
    NODES+=1
    if NODES>=BUDGET:raise TO
    a0=alpha
    ent=TT.get(KEY)
    ttm=None
    if ent:
        ttm=ent[3]
        if ent[0]>=depth:
            if ent[1]==0:return ent[2]
            if ent[1]==1:alpha=max(alpha,ent[2])
            else:beta=min(beta,ent[2])
            if alpha>=beta:return ent[2]
    inchk=att(KP[TURN],-TURN)
    if inchk:depth+=1
    best=-INF;bm=None;legal=0
    for m in order(moves(),ttm,ply):
        u=make(m)
        if att(KP[-TURN],TURN):
            unmake(u);continue
        legal+=1
        if depth>=3 and legal>=4 and not inchk and not B[m[1]] and not m[2] and m[1]!=EP:
            sc=-search(depth-2,-alpha-1,-alpha,ply+1)
            if sc>alpha:sc=-search(depth-1,-beta,-alpha,ply+1)
        else:
            sc=-search(depth-1,-beta,-alpha,ply+1)
        unmake(u)
        if sc>best:best=sc;bm=m
        if sc>alpha:alpha=sc
        if alpha>=beta:
            if not B[m[1]] and not m[2] and m[1]!=EP:
                kk=KILL[ply]
                if kk[0]!=m:kk[1]=kk[0];kk[0]=m
                h=(TURN,m[0],m[1])
                HIST[h]=min(70000,HIST.get(h,0)+depth*depth)
            break
    if not legal:
        return -MATE+ply if inchk else 0
    fl=2 if best<=a0 else 1 if best>=beta else 0
    TT[KEY]=(depth,fl,best,bm)
    return best

def parse_uci(u):
    s=(8-int(u[1]))*8+(ord(u[0])-97)
    t=(8-int(u[3]))*8+(ord(u[2])-97)
    pr={"n":2,"b":3,"r":4,"q":5}[u[4]] if len(u)>4 else 0
    return (s,t,pr)

def uci(m):
    s,t,pr=m
    o="abcdefgh"[s&7]+str(8-(s>>3))+"abcdefgh"[t&7]+str(8-(t>>3))
    return o+("nbrq"[pr-2] if pr else "")

def parse_fen(fen):
    global TURN,CAST,EP,KEY,PHASE
    f=fen.split()
    mp={"p":1,"n":2,"b":3,"r":4,"q":5,"k":6}
    for s in range(64):B[s]=0
    for r,row in enumerate(f[0].split("/")):
        x=0
        for ch in row:
            if ch.isdigit():x+=int(ch)
            else:
                B[r*8+x]=mp[ch.lower()]*(1 if ch.isupper() else -1)
                x+=1
    TURN=1 if f[1]=="w" else -1
    CAST=0
    for ch,b in(("K",1),("Q",2),("k",4),("q",8)):
        if ch in f[2]:CAST|=b
    EP=-1
    if len(f)>3 and f[3]!="-":EP=(8-int(f[3][1]))*8+(ord(f[3][0])-97)
    KEY=0;PHASE=0
    for s in range(64):
        p=B[s]
        if p:
            KEY^=Z[p+6][s]
            a=abs(p)
            if a==6:KP[1 if p>0 else -1]=s
            elif a in(2,3):PHASE+=1
            elif a==4:PHASE+=2
            elif a==5:PHASE+=4
    if TURN<0:KEY^=ZS
    KEY^=ZC[CAST]
    if EP>=0:KEY^=ZE[EP&7]

def hist_keys(g):
    parse_fen(g["start_fen"])
    ks={KEY}
    for u in g["moves"]:
        make(parse_uci(u))
        ks.add(KEY)
    return ks

def choose(fen,legal,hist):
    global NODES,GKEYS
    parse_fen(fen)
    GKEYS=hist
    NODES=0
    roots=[parse_uci(u) for u in legal]
    if len(roots)==1:return roots[0]
    best=roots[0]
    depth=1
    while depth<=64:
        try:
            alpha=-INF;cb=None
            for m in order(roots,best,0):
                u=make(m)
                if att(KP[-TURN],TURN):
                    unmake(u);continue
                sc=-search(depth-1,-INF,-alpha,1)
                unmake(u)
                if sc>alpha:alpha=sc;cb=m
            if cb is not None:best=cb
        except TO:
            break
        depth+=1
    return best

def post(path,body):
    req=urllib.request.Request(U+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
    try:
        with urllib.request.urlopen(req) as res:return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code}")

while True:
    g=post("/game",{})
    if g["status"]=="done":break
    while g["status"]=="your_move":
        try:
            mv=uci(choose(g["fen"],g["legal_moves"],hist_keys(g)))
            if mv not in g["legal_moves"]:mv=g["legal_moves"][0]
        except Exception:
            mv=g["legal_moves"][0]
        g=post("/move",{"game":g["game"],"move":mv})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)
