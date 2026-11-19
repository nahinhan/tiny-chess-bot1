import json,os,sys,urllib.error,urllib.request
U=os.environ.get('MAKEFUN_ENV_URL')or sys.exit('MAKEFUN_ENV_URL is not set')
def post(p,b):
 r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={'content-type':'application/json'})
 try:
  with urllib.request.urlopen(r)as s:return json.load(s)
 except urllib.error.HTTPError as e:sys.exit(f'{p}: HTTP {e.code} {e.read().decode(errors="replace")}')
V={'P':100,'N':320,'B':330,'R':500,'Q':900,'K':20000,'p':-100,'n':-320,'b':-330,'r':-500,'q':-900,'k':-20000}
PST={'P':[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],'N':[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],'B':[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],'R':[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],'Q':[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],'K':[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]}
D={'N':(-33,-31,-18,-14,14,18,31,33),'B':(-17,-15,15,17),'R':(-16,-1,1,16),'Q':(-17,-16,-15,-1,1,15,16,17),'K':(-17,-16,-15,-1,1,15,16,17)}
def parse(fen):
 p=fen.split();b=[None]*128;r=0;f=0
 for c in p[0]:
  if c=='/':r+=1;f=0
  elif c.isdigit():f+=int(c)
  else:b[r*16+f]=c;f+=1
 ep=-1 if p[3]=='-'else(8-int(p[3][1]))*16+(ord(p[3][0])-97)
 return b,1 if p[1]=='w'else-1,p[2],ep
def sq(s):(8-int(s[1]))*16+(ord(s[0])-97)
def ev(b,sd):
 sc=0
 for r in range(8):
  for f in range(8):
   x=b[r*16+f]
   if x:
    u=x.upper();i=r*8+f if x.isupper()else(7-r)*8+f
    sc+=V[x]+(PST[u][i]if x.isupper()else-PST[u][i])
 return sc*sd
def gen(b,sd,ep,caps=0):
 ms=[]
 for r in range(8):
  for f in range(8):
   s=r*16+f;x=b[s]
   if not x or(1 if x.isupper()else-1)!=sd:continue
   u=x.upper()
   if u=='P':
    st=-16 if sd==1 else 16;sr=6 if sd==1 else 1;pr=0 if sd==1 else 7;t=s+st
    if not caps and not(t&136)and not b[t]:
     if(t>>4)==pr:
      for q in'qrbn':ms.append((s,t,q if sd==-1 else q.upper()))
     else:
      ms.append((s,t,''))
      if r==sr and not b[t+st]:ms.append((s,t+st,''))
    for df in(-1,1):
     t=s+st+df
     if not(t&136):
      y=b[t]
      if(y and(1 if y.isupper()else-1)==-sd)or t==ep:
       if(t>>4)==pr:
        for q in'qrbn':ms.append((s,t,q if sd==-1 else q.upper()))
       else:ms.append((s,t,''))
   else:
    sl=u in'BRQ'
    for d in D[u]:
     t=s+d
     while not(t&136):
      y=b[t]
      if not y:
       if not caps:ms.append((s,t,''))
      else:
       if(1 if y.isupper()else-1)==-sd:ms.append((s,t,''))
       break
      if not sl:break
      t+=d
 return ms
def mk(b,m,ep):
 nb=b[:];s,t,pr=m;x=nb[s];nb[s]=None
 if x in'Pp'and t==ep:nb[t+(16 if x=='P'else-16)]=None
 if x in'Kk'and abs(t-s)==2:
  if t>s:nb[t-1]=nb[t+1];nb[t+1]=None
  else:nb[t+1]=nb[t-2];nb[t-2]=None
 nb[t]=pr if pr else x;return nb
def ordm(b,ms):
 def k(m):
  v=b[m[1]];s=(abs(V[v])*10-abs(V[b[m[0]]]))if v else 0
  if m[2]:s+=800
  return -s
 return sorted(ms,key=k)
def qsearch(b,sd,al,be,ep):
 st=ev(b,sd)
 if st>=be:return be
 if st>al:al=st
 for m in ordm(b,gen(b,sd,ep,1)):
  v=b[m[1]]
  if v and v.upper()=='K':return 29000
  sc=-qsearch(mk(b,m,-1),-sd,-be,-al,-1)
  if sc>=be:return be
  if sc>al:al=sc
 return al
def search(b,sd,dp,al,be,ep):
 if dp<=0:return qsearch(b,sd,al,be,ep)
 ms=ordm(b,gen(b,sd,ep,0))
 if not ms:return ev(b,sd)
 best=-30000
 for m in ms:
  v=b[m[1]]
  if v and v.upper()=='K':return 29000+dp
  nep=m[0]+(-8 if sd==1 else 8)if b[m[0]]in'Pp'and abs(m[1]-m[0])==32 else -1
  sc=-search(mk(b,m,ep),-sd,dp-1,-be,-al,nep)
  if sc>best:best=sc
  if sc>al:al=sc
  if al>=be:break
 return best
def choose(fen,legal):
 if len(legal)==1:return legal[0]
 b,sd,_,ep=parse(fen);bm=legal[0];bs=-31000
 rms=[(sq(u[:2]),sq(u[2:4]),(u[4].upper()if sd==1 else u[4].lower())if len(u)==5 else'',u)for u in legal]
 rms.sort(key=lambda m:-(abs(V[b[m[1]]])*10 if b[m[1]]else 0)-(800 if m[2]else 0))
 for s,t,pr,u in rms:
  nb=mk(b,(s,t,pr),ep)
  nep=s+(-8 if sd==1 else 8)if b[s]in'Pp'and abs(t-s)==32 else -1
  sc=-search(nb,-sd,2,-31000,-bs,nep)
  if sc>bs:bs=sc;bm=u
 return bm
while True:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)
