import pyomo.environ as pyo
import numpy as np
from pyomo.environ import log
import time

name = ['室蘭市', '苫小牧市', '登別市', '伊達市', '豊浦町', '壮瞥町', '白老町', '厚真町', '洞爺湖町', '安平町', 'むかわ町']
waste = [ 20448 , 42288 , 11426 , 6907 , 641 , 983 , 3395 , 458 , 2163 ,  972 , 624 ]
distance = [0, 66, 17, 24, 42, 35, 43, 98, 36, 89, 99, 66, 0, 50, 85, 102, 85, 24, 32, 97, 24, 34, 17, 50, 0, 34, 54, 47, 27, 82, 48, 73, 83, 24, 85, 34, 0, 19, 12, 62, 123, 13, 113, 126, 42, 102, 54, 19, 0, 19, 80, 131, 6, 121, 133, 35, 85, 47, 12, 19, 0, 73, 113, 14, 103, 116, 43, 24, 27, 62, 80, 73, 0, 56, 74, 47, 57, 98, 32, 82, 123, 131, 113, 56, 0, 125, 10, 18, 36, 97, 48, 13, 6, 14, 74, 125, 0, 125, 128, 89, 24, 73, 113, 121, 103, 47, 10, 125, 0, 28, 99, 34, 83, 126, 133, 116, 57, 18, 128, 28, 0]

##initialize、boundsの設定
m = pyo.ConcreteModel(name="iburimodel", doc="(len(distance)+len(waste)) variables , (len(waste)+3) constraints")
m.x = pyo.Var( list(range(len(distance))), domain = pyo.NonNegativeReals,bounds=(0,350000), initialize = 10 )
m.y = pyo.Var( list(range(len(waste))), domain = pyo.Binary, initialize = 0 )

##log=ln, ICは÷供用年数25年
TC = sum( m.y[i] * ( sum(m.x[j] * distance[j] for j in range(i*len(waste), (i+1)*len(waste)) ) * 300 /10000 ) for i in range(len(waste)) )
IC = sum( m.y[i] * 21341 * ((sum( m.x[j] for j in range(i*len(waste), (i+1)*len(waste)) )/365) ** (-0.279)) * sum( m.x[j] for j in range(i*len(waste), (i+1)*len(waste)) )/365 for i in range(len(waste)) ) /25
OC = sum( m.y[i] * (-5412 * log( sum( m.x[j] for j in range(i*len(waste), (i+1)*len(waste)) ) /365) +36088) * sum( m.x[j] for j in range(i*len(waste), (i+1)*len(waste)) ) /10000 for i in range(len(waste)) )

m.OBJ = pyo.Objective(expr =  TC + IC + OC  , sense = pyo.minimize )

##施設は１個以上、市町村数以下
# == aでやるとa.99999 == a+1 施設になってしまう
m.c1 = pyo.Constraint( expr = sum( m.y[i] for i in range(len(waste)) ) >= 1 )
m.c2 = pyo.Constraint( expr = sum( m.y[i] for i in range(len(waste)) ) <= len(waste) )

##そこから輸送する合計(縦)＝そこの発生ごみ量
m.c3 = pyo.ConstraintList()
for i in range(len(waste)):
    m.c3.add( expr = sum( m.x[j] for j in range(i, len(distance)-len(waste)+i+1, len(waste)) ) == waste[i] )

##施設のない所には輸送されない＝（施設がある所に輸送される量の全施設合計＝ごみ合計となる）
m.c4 = pyo.Constraint( expr = sum( m.y[i] * sum(m.x[j] for j in range(i*len(waste), (i+1)*len(waste)) ) for i in range(len(waste)) ) - sum( waste[i] for i in range(len(waste)) ) == 0 )


opt = pyo.SolverFactory('ipopt')
start_time = time.perf_counter()

for i in range(2):
    print(i)
    res = opt.solve(m)

end_time = time.perf_counter()
elapsed_time = end_time - start_time


for i in range(len(waste)):
    print(f"y{i}: {m.y[i].value:.0f}")

xmat = []
for i in range(len(waste)):
    xlist = []
    for j in range(i*len(waste), (i+1)*len(waste)):
        xlist.append(round(m.x[j]()))
        xmat.append(xlist)

print(np.array(xmat))


print(f"輸送コスト：{TC()}")
print(f"建設コスト：{IC()}")
print(f"運営コスト：{OC()}")

print(f"総コスト：{m.OBJ()}")
print(f"確認：{TC()+IC()+OC()}")

print(f"実行時間＝ {round(elapsed_time/1)}s")

