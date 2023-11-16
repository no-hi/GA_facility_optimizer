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

TClist  = []
ATClist  = []
BTClist  = []

IClist  = []
AIClist  = []
BIClist  = []

OClist  = []
AOClist  = []
BOClist  = []

AXlist  = []
BXlist  = []

###市町村指定ーーーー
select1 = '札幌市'
###ーーーーーーーーー


def make_dlist(k):
  dmat = []
  for i in range(len(waste)):
    dlist = []
    for j in range(i*len(waste), (i+1)*len(waste)):
      dlist.append(distance[j])
    dmat.append(dlist)

  dmat2 = [dmat[name.index(select1)],dmat[k]]

  return dmat2


for k in range(len(waste)):
  print(k)
  ##initialize、boundsの設定ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
  m = pyo.ConcreteModel()
  m.ax = pyo.Var( list(range(len(waste))), domain = pyo.NonNegativeReals, initialize = 1 )
  m.bx = pyo.Var( list(range(len(waste))), domain = pyo.NonNegativeReals, initialize = 1 )
  ##ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
  
  dmat2 = make_dlist(k)
  dlist1 = dmat2[0]
  dlist2 = dmat2[1]

  ## AX　900600
  ATC = sum((m.ax[j]) * dlist1[j] for j in range(len(waste))) * 300 /10000
  AIC = (21341 * (900) ** (-0.279)) * sum( m.ax[j] for j in range(len(waste))) /365 /25
  AOC = (-5412 * log(600) +36088) * sum(m.ax[j] for j in range(len(waste))) /10000

  ## BX  900600  ## ax→bx注意
  BTC = sum((m.bx[j]) * dlist2[j] for j in range(len(waste))) * 300 /10000
  BIC = (21341 * (900) ** (-0.279)) * (sum( m.bx[j] for j in range(len(waste))) /365) /365 /25
  BOC = (-5412 * log(600) +36088) * sum(m.bx[j] for j in range(len(waste))) /10000

  AC  = ATC+AIC+AOC
  BC  = BTC+BIC+BOC

  m.OBJ = pyo.Objective(expr = AC+BC , sense = pyo.minimize )


  #そこから輸送する合計(縦)=そこの発生ごみ量
  # (ax+bx+cx+...)
  m.c3 = pyo.ConstraintList()
  for i in range(len(waste)):
    m.c3.add( expr = (m.ax[i]+m.bx[i]) == waste[i] )
  
  
  opt = pyo.SolverFactory('ipopt')
  opt.options["tol"] = 1E-1
  #opt.options['max_iter'] = 80
  #iburiなら30
  #for i in range(2):
  for i in range(1):
    res = opt.solve(m)

  end_time = time.perf_counter()
  elapsed_time = end_time - start_time


  axlist = []
  for j in range(len(waste)):
    axlist.append(round(m.ax[j]()))

  bxlist = []
  for j in range(len(waste)):
    bxlist.append(round(m.bx[j]()))


  TC = ATC+BTC
  IC = AIC+BIC
  OC = AOC+BOC
  

  AXlist.append(axlist)
  BXlist.append(bxlist)
  
  TClist.append(round(TC()))
  ATClist.append(round(ATC()))
  BTClist.append(round(BTC()))
  
  IClist.append(round(IC()))
  AIClist.append(round(AIC()))
  BIClist.append(round(BIC()))
  
  OClist.append(round(OC()))
  AOClist.append(round(AOC()))
  BOClist.append(round(BOC()))

  AClist.append(round(AC()))
  BClist.append(round(BC()))
  OBJlist.append(m.OBJ())
  OBJIntegerlist.append(round(m.OBJ()))

#print("ーーーAーーー")
#print(np.array(AXlist))
#print("\n\nーーーBーーー")
#print(np.array(BXlist))
#print("\n\nーーー輸送コストーーー")
#print(np.array(TClist))
#print("\n\nーーー建設コストーーー")
#print(np.array(IClist))
#print("\n\nーーー運営コストーーー")
#print(np.array(OClist))
#print("\n\nーーー総コストーーー")
#print(np.array(OBJIntegerlist))

print("\n\nーーーーーーー最小ーーーーーーー")
print("select="+select1)
print(f"総コスト:{min(OBJlist)}")
print(f"輸送コスト:{TClist[OBJlist.index(min(OBJlist))]}")
print(f"建設コスト:{IClist[OBJlist.index(min(OBJlist))]}")
print(f"運営コスト:{OClist[OBJlist.index(min(OBJlist))]}")

print("\nーーーA="+select1+"ーーー")
print(f"A:{np.array(AXlist[OBJlist.index(min(OBJlist))])}")
print(f"A規模:{round(sum(AXlist[OBJlist.index(min(OBJlist))])/365)}(t/day)、{round(sum(AXlist[OBJlist.index(min(OBJlist))]))}(t/年)")
print(f"AC:{AClist[OBJlist.index(min(OBJlist))]}")
print(f"ATC:{ATClist[OBJlist.index(min(OBJlist))]}")
print(f"AIC:{AIClist[OBJlist.index(min(OBJlist))]}")
print(f"AOC:{AOClist[OBJlist.index(min(OBJlist))]}")

print("\nーーーB="+name[OBJlist.index(min(OBJlist))]+"ーーー")
print(np.array(BXlist[OBJlist.index(min(OBJlist))]))
print(f"B規模:{round(sum(BXlist[OBJlist.index(min(OBJlist))])/365)}(t/day)、{round(sum(BXlist[OBJlist.index(min(OBJlist))]))}(t/年)")
print(f"BC:{BClist[OBJlist.index(min(OBJlist))]}")
print(f"BTC:{BTClist[OBJlist.index(min(OBJlist))]}")
print(f"BIC:{BIClist[OBJlist.index(min(OBJlist))]}")
print(f"BOC:{BOClist[OBJlist.index(min(OBJlist))]}")

print(f"\n実行時間= {round(elapsed_time/1)}秒\n\n")








