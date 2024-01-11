daily_trans_size=45

CAR_trans = round(daily_trans_size / 10)
# CT＝建設費、CB＝車両購入費
C_T = float(3*10**8 * (daily_trans_size / 100)**0.7 /20) /10000
C_T2= 216468*daily_trans_size**(-0.643)*1000*daily_trans_size/20/10000
C_B = float((1+0.4)*10**7 *CAR_trans /7) /10000
IC_TRANS = C_T+C_B

# CM=整備補修費、CP=人件費、CE=電気使用料、CW=水道費
C_M = float(1.344*10**6 * CAR_trans +0.4*C_T) /10000
C_P = float(7*10**6 * (4 + int(3*daily_trans_size/100 - 1))) /10000
C_Pn= (4 + int(3*daily_trans_size/100 - 1))
# /100

# 2021日本産業用平均電気価格＝19.28円/kWh
C_E = float(6200*19.28*daily_trans_size) /10000
# 水道代=300円/m3（松藤中継資料のエクセルの通り）
C_W = float(93*300*CAR_trans) /10000
OC_TRANS = C_M + C_P + C_E + C_W

print(f"C_T={round(C_T*20/10000,2)}億円")
print(f"C_T2={round(C_T2*20/10000,2)}億円")
print(f"C_B={C_B}")
print(f"C_M={C_M}")
print(f"C_P={C_P}")
print(f"人数={C_Pn}")
print(f"C_E={C_E}")
print(f"C_W={C_W}")
