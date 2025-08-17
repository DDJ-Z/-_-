import pandas as pd
df = pd.read_csv(r'C:\Users\86136\Desktop\HF\CourseDesign\data\pdata.csv',encoding='gbk')
all_rows = df.values.tolist()
'''all_rows第零行为例子,数据含义是all_rows[0][0]是时间,all_rows[0][1]是E0, 2,3,4,5是P1,P2,P3,P4'''
CT = [[0] * 18 for i in range(len(all_rows))]
'''第零行为例子,CT[0][0]是Ep,CT[0][1]是P,2是EU,3是EL,4是ED,5是E,6是PE,7是WU,8是WL,9是WD,10是W,11是R_perv,12是Rg,13是Rs,14是R,15是Qs,16是Qg,17是Q'''
WUM=20
WLM=70
WDM=50
C=0.16
b=0.2
WM=140
IM=0.001
FC=10.4
WMM=(1+b)*WM/(1-IM)
#单位线
UH = [0,40,80,130,100,80,48,20,10,5,0]
#消退系数
CG = 0.98
#初始地下径流
QG0 = 55.3
CT[0][7] = 10
CT[0][8] = 70
CT[0][9] = 50
CT[0][10] = 130
KC=1.05
def EU(wu:float,p:float,ep:float):
    if wu + p >= ep:
        EU = round(ep, 1)
    else:
        EU = round(wu + p,1)
    return EU
def EL(wl:float,ep:float,eu:float):
    if wl >= C * WLM:
        EL = round((ep - eu) * wl / WLM, 1)
    elif  wl >= (ep - eu) * C and wl < C * WLM:
        EL=round((ep - eu) * C,1)
    elif wl < (ep - eu) * C:
        EL= round(wl,1)
    else:
        EL= round(0,1)
    return EL
def ED(wl:float,ep:float,eu:float,el:float):
    if wl< ((ep - eu) * C):
        ED = round(((ep - eu) * C) - el, 2)
    else:
        ED = round(0,1)
    return ED
def WUC(p:float,eu:float,wu:float,R:float):
    if p - eu + wu - R < WUM:
        WUC = round(p - eu + wu - R, 1)
    elif  p - eu + wu - R >= WUM:
        WUC = round(WUM, 1)
    if WUC<0:
        WUC = round(0,1)
    return WUC
def WLC(p:float,eu:float,el:float,wu:float,wl:float,R:float,):
    if p - eu + wu - R < WUM:
        WLC = round(wl - el, 1)
    elif p - eu + wu - R >= WUM and wl - el + (p - eu + wu - R) - WUM < WLM:
        WLC = round(wl - el + (p - eu + wu - R) - WUM, 1)
    elif wl - el + (p - eu + wu - R) - WUM >= WLM:
        WLC = round(WLM, 1)
    if WLC<0:
        WLC = round(0,1)
    return WLC
def WDC(p:float,eu:float,el:float,ed:float,wu:float,wl:float,wd:float,R:float):
    if wl - el + (p - eu + wu - R) - WUM < WLM:
        WDC = round(wd - ed, 1)
    elif wl - el + (p - eu + wu - R) - WUM >= WLM and wd - ed + wl - el + (p - eu + wu - R) - WUM - WLM < WDM:
        WDC = round(wd - ed + wl - el + (p - eu + wu - R) - WUM - WLM, 1)
    elif wd - ed + wl - el + (p - eu + wu - R) - WUM - WLM >= WDM:
        WDC = round(WDM, 1)
    if WDC<0:
        WDC = round(0, 1)
    return WDC
def R_pervC(w,pe):
    if pe <= 0:
        RC = 0
    else:
        a = WMM * (1 - ((1 - (w / WM))**(1/(1 + b))))
        if a + pe <=WMM:
            RC = pe + w - WM + WM * ((1 - ((pe + a) / WMM))**(b + 1))
        elif a + pe > WMM:
            RC = pe-(WM-w)
    return RC
def TwoR(pe,R):
    #参数R是按蓄水容量面积曲线算出来的径流量
    RB = pe*IM#RB是不透水区域产流
    if pe >= FC:
        Rg = FC*( R/pe)#地表径流
        Rs = R - Rg + RB#地下径流
    else:
        Rs = RB
        Rg = R
    Rl = [Rg,Rs]
    return Rl
def QS(Rsl,UH):
    QSlen = len(Rsl) +len(UH) - 1
    QS = [0]*QSlen
    for i in range(QSlen):
        for j in range(len(UH)):
            if 0 <= i-j < len(Rsl):
                QS[i] += (Rsl[i-j]/10) * UH[j]
    return QS
def QG(Rgl):
    QG = [0]*(len(Rgl) + 1)
    QG[0] = QG0
    for i in range(1,len(QG)):
        QG[i] = CG*QG[i-1] + (1-CG)*Rgl[i-1]*(553/(3.6*3))
    return QG[1:]

for i in range(len(CT)):
    CT[i][0] = round(all_rows[i][1] * KC, 1)
    CT[i][1] = round(all_rows[i][2] * 0.33 + all_rows[i][3] * 0.14 + all_rows[i][4] * 0.33 + all_rows[i][5] * 0.20, 1)
for i in range(len(CT)):
    if i == 0:
        CT[i][2] = EU(CT[i][7], CT[i][1], CT[i][0])
        CT[i][3] = EL(CT[i][8], CT[i][0], CT[i][2])
        CT[i][4] = ED(CT[i][8], CT[i][0], CT[i][2], CT[i][3])
        CT[i][5] = round(sum(CT[i][2:5]), 1)
        CT[i][6] = round(CT[i][1] - CT[i][5], 1)
        CT[i][11] = round(R_pervC(CT[i][10], CT[i][6]),1)
        CT[i][12] = round(TwoR(CT[i][6],CT[i][11])[0],1)
        CT[i][13] = round(TwoR(CT[i][6], CT[i][11])[1],1)
        CT[i][14] = CT[i][12] + CT[i][13]
    else:
        CT[i][7] = WUC(CT[i - 1][1], CT[i - 1][2], CT[i - 1][7], CT[i - 1][11])
        CT[i][8] = WLC(CT[i - 1][1], CT[i - 1][2], CT[i - 1][3], CT[i - 1][7], CT[i - 1][8], CT[i - 1][11])
        CT[i][9] = WDC(CT[i - 1][1], CT[i - 1][2], CT[i - 1][3], CT[i - 1][4], CT[i - 1][7], CT[i - 1][8], CT[i - 1][9],
                       CT[i - 1][11])
        CT[i][10] = round(sum(CT[i][7:10]), 1)
        CT[i][2] = EU(CT[i][7], CT[i][1], CT[i][0])
        CT[i][3] = EL(CT[i][8], CT[i][0], CT[i][2])
        CT[i][4] = ED(CT[i][8], CT[i][0], CT[i][2], CT[i][3])
        CT[i][5] = round(sum(CT[i][2:5]), 1)
        CT[i][6] = round(CT[i][1] - CT[i][5], 1)
        CT[i][11] = round(R_pervC(CT[i][10], CT[i][6]), 1)
        CT[i][12] = round(TwoR(CT[i][6], CT[i][11])[0], 1)
        CT[i][13] = round(TwoR(CT[i][6], CT[i][11])[1], 1)
        CT[i][14] = CT[i][12] + CT[i][13]
Rsl = []
Rgl = []
for i in range(len(CT)):
    Rsl.append(CT[i][13])
    Rgl.append(CT[i][12])
Qsl = QS(Rsl,UH)
Qgl = QG(Rgl)
for i in range(len(CT)):
    CT[i][15] = round(Qsl[i],1)
    CT[i][16] = round(Qgl[i],1)
    CT[i][17] = CT[i][15]+CT[i][16]
for i in range(len(CT)):
    CT[i].append(all_rows[i][0])
excel = pd.DataFrame(CT,columns=['Ep','P(mm)','EU','EL','ED','E','PE','WU','WL','WD','W','R_perv','Rg(mm)','Rd(mm)','R(mm)','Qd(m³/s)','Qg(m³/s)','Q(m³/s)','时间'])
path = r'C:\Users\86136\Desktop\HF\CourseDesign\twowater.xlsx'
selected_columns = ['时间','P(mm)','Rd(mm)','Rg(mm)','R(mm)','Qd(m³/s)','Qg(m³/s)','Q(m³/s)']
excel_selscted = excel[selected_columns]
excel_selscted.to_excel(path,index=False,engine='openpyxl')