import pyomo.environ as pyo
import numpy as np
np.set_printoptions(threshold=np.inf)
from pyomo.environ import log
from pyomo.environ import log10
import time
import data
start_time = time.perf_counter()


name = data.hokkaido
waste = data.kanen
distance = data.distance


OBJIntegerlist = []
OBJlist = []

AClist  = []
BClist  = []
CClist  = []

TClist  = []
ATClist  = []
BTClist  = []
CTClist  = []

IClist  = []
AIClist  = []
BIClist  = []
CIClist  = []

OClist  = []
AOClist  = []
BOClist  = []
COClist  = []

AXlist  = []
BXlist  = []
CXlist  = []

###市町村指定ーーーー
select1 = '札幌市'
select2 = '函館市'
select3 = '本別町'
###ーーーーーーーーー


def make_dlist():
  dmat = []
  for i in range(len(waste)):
    dlist = []
    for j in range(i*len(waste), (i+1)*len(waste)):
      dlist.append(distance[j])
    dmat.append(dlist)

  dmat3 = [dmat[name.index(select1)],dmat[name.index(select2)],dmat[name.index(select3)]]
  
  return dmat3


for k in range(3):
  print(k)

  dmat3 = make_dlist()
  dlist1 = dmat3[0]
  dlist2 = dmat3[1]
  dlist3 = dmat3[2]
  
  
  ##initialize、boundsの設定ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
  m = pyo.ConcreteModel()
  m.ax = pyo.Var( list(range(len(waste))), domain = pyo.NonNegativeReals, initialize = 1 )
  m.bx = pyo.Var( list(range(len(waste))), domain = pyo.NonNegativeReals, initialize = 1 )
  m.cx = pyo.Var( list(range(len(waste))), domain = pyo.NonNegativeReals, initialize = 1 )
  ##ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

  
  ## AX　札幌は900600でいい
  ATC = sum((m.ax[j]) * dlist1[j] for j in range(len(waste))) * 300 /10000
  AIC = (21341 * (900) ** (-0.279)) * (sum(m.ax[j] for j in range(len(waste))) /365) /25
  AOC = (-5412 * log(600) +36088) * sum(m.ax[j] for j in range(len(waste))) /10000

  ## BX   ## ax→bx、dlist 注意
  BTC = sum((m.bx[j]) * dlist2[j] for j in range(len(waste))) * 300 /10000
  BIC = ( 21341 * ((sum( m.bx[j] for j in range(len(waste)) )/365) ** (-0.279)) * sum( m.bx[j] for j in range(len(waste)) )/365) /25
  BOC = (-5412 * log( sum(m.cx[j] for j in range(len(waste)) ) /365) +36088) * sum( m.bx[j] for j in range(len(waste)) ) /10000

  ## CX   ## ax→bx、dlist 注意
  CTC = sum((m.cx[j]) * dlist3[j] for j in range(len(waste))) * 300 /10000
  CIC = ( 21341 * ((sum( m.cx[j] for j in range(len(waste)) )/365) ** (-0.279)) * sum( m.cx[j] for j in range(len(waste)) )/365) /25
  COC = (-5412 * log( sum(m.cx[j] for j in range(len(waste)) ) /365) +36088) * sum( m.cx[j] for j in range(len(waste)) ) /10000

  
  AC  = ATC+AIC+AOC
  BC  = BTC+BIC+BOC
  CC  = CTC+CIC+COC

  m.OBJ = pyo.Objective(expr = AC+BC+CC , sense = pyo.minimize )


  #そこから輸送する合計(縦)＝そこの発生ごみ量
  # (ax+bx+cx+...)
  m.c3 = pyo.ConstraintList()
  for i in range(len(waste)):
    m.c3.add( expr = (m.ax[i]+m.bx[i]+m.cx[i]) == waste[i] )
  
  ##tee=True のAMPLエラーが原因
  opt = pyo.SolverFactory('ipopt')
  opt.options["tol"] = 1E-1
  #opt.options['max_iter'] = 100
  #iburiなら30  #tee=Trueで調べる
  #for i in range(2):
  for i in range(1):
    res = opt.solve(m)


  axlist = []
  for j in range(len(waste)):
    axlist.append(round(m.ax[j]()))

  bxlist = []
  for j in range(len(waste)):
    bxlist.append(round(m.bx[j]()))

  cxlist = []
  for j in range(len(waste)):
    cxlist.append(round(m.cx[j]()))

 
  TC = ATC+BTC+CTC
  IC = AIC+BIC+CIC
  OC = AOC+BOC+COC
  

  AXlist.append(axlist)
  BXlist.append(bxlist)
  CXlist.append(cxlist)
  
  TClist.append(round(TC()))
  ATClist.append(round(ATC()))
  BTClist.append(round(BTC()))
  CTClist.append(round(CTC()))
  
  IClist.append(round(IC()))
  AIClist.append(round(AIC()))
  BIClist.append(round(BIC()))
  CIClist.append(round(CIC()))
  
  OClist.append(round(OC()))
  AOClist.append(round(AOC()))
  BOClist.append(round(BOC()))
  COClist.append(round(COC()))

  AClist.append(round(AC()))
  BClist.append(round(BC()))
  CClist.append(round(CC()))
  
  OBJlist.append(m.OBJ())
  OBJIntegerlist.append(round(m.OBJ()))


#print("\n\nーーー輸送コストーーー")
#print(np.array(TClist))
#print("\n\nーーー建設コストーーー")
#print(np.array(IClist))
#print("\n\nーーー運営コストーーー")
#print(np.array(OClist))
#print("\n\nーーー総コストーーー")
#print(np.array(OBJIntegerlist))


end_time = time.perf_counter()
elapsed_time = end_time - start_time

print("\n\nーーーーーーー最小ーーーーーーー")
print("select="+select1+"＋"+select2+"＋"+select3)
print(f"総コスト：{min(OBJlist)}")
print(f"輸送コスト：{TClist[OBJlist.index(min(OBJlist))]}")
print(f"建設コスト：{IClist[OBJlist.index(min(OBJlist))]}")
print(f"運営コスト：{OClist[OBJlist.index(min(OBJlist))]}")

print("\nーーーA="+select1+"ーーー")
print(np.array(AXlist[OBJlist.index(min(OBJlist))]))
print(f"A規模：{round(sum(AXlist[OBJlist.index(min(OBJlist))])/365)}(t/day)、{round(sum(AXlist[OBJlist.index(min(OBJlist))]))}(t/年)")
print(f"AC：{AClist[OBJlist.index(min(OBJlist))]}")
print(f"ATC：{ATClist[OBJlist.index(min(OBJlist))]}")
print(f"AIC：{AIClist[OBJlist.index(min(OBJlist))]}")
print(f"AOC：{AOClist[OBJlist.index(min(OBJlist))]}")

print("\nーーーB="+select2+"ーーー")
print(np.array(BXlist[OBJlist.index(min(OBJlist))]))
print(f"B規模：{round(sum(BXlist[OBJlist.index(min(OBJlist))])/365)}(t/day)、{round(sum(BXlist[OBJlist.index(min(OBJlist))]))}(t/年)")
print(f"BC：{BClist[OBJlist.index(min(OBJlist))]}")
print(f"BTC：{BTClist[OBJlist.index(min(OBJlist))]}")
print(f"BIC：{BIClist[OBJlist.index(min(OBJlist))]}")
print(f"BOC：{BOClist[OBJlist.index(min(OBJlist))]}")

print("\nーーーC="+select3+"ーーー")
print(np.array(CXlist[OBJlist.index(min(OBJlist))]))
print(f"C規模：{round(sum(CXlist[OBJlist.index(min(OBJlist))])/365)}(t/day)、{round(sum(CXlist[OBJlist.index(min(OBJlist))]))}(t/年)")
print(f"CC：{CClist[OBJlist.index(min(OBJlist))]}")
print(f"CTC：{CTClist[OBJlist.index(min(OBJlist))]}")
print(f"CIC：{CIClist[OBJlist.index(min(OBJlist))]}")
print(f"COC：{COClist[OBJlist.index(min(OBJlist))]}")


print(f"\n実行時間＝ {round(elapsed_time/1)}秒 ＝ {round(elapsed_time/60)}分 \n\n")
