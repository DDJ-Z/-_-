import pandas as pd
df = pd.read_csv(r'C:\Users\86136\Desktop\HF\CourseDesign\data\pdata.csv',encoding='gbk')
all_rows = df.values.tolist()
'''all_rows第零行为例子,数据含义是all_rows[0][0]是时间,all_rows[0][1]是E0, 2,3,4,5是P1,P2,P3,P4'''
CT = [[0] * 20 for i in range(len(all_rows))]
'''第零行为例子,CT[0][0]是Ep,CT[0][1]是P,2是EU,3是EL,4是ED,5是E,6是PE,7是WU,8是WL,9是WD,10是W,11是R总,12是RS,13是RI,14是RG,15是S_1,16是Qs,17是Qi,18是Qg,19是Q'''
WUM=20
WLM=70
WDM=50
C=0.16
b=0.2
KC = 1.05
IM=0.001
WM=140
WMM=(1+b)*WM/(1-IM)
F = 553 #平方千米
SM = 18
EX = 1.4
SMM = SM*(1+EX)
KI = 0.3
KG = 0.4
CS = 0.8
CI = 0.92
CG = 0.98
S0 = 0
QS0 = 0
QI0 = 0
QG0 = 55.3
CT[0][7] = 10
CT[0][8] = 70
CT[0][9] = 50
CT[0][10] = 130
R_a = sum(all_rows[i][1] for i in range(len(all_rows)))*(24*3600)/(553*1000) #mm
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
def RC(w,pe):
    if pe <= 0:
        RC = round(0,1)
    else:
        RB = pe * IM  # RB是不透水区域产流
        a = WMM * (1 - ((1 - (w / WM))**(1/(1 + b))))
        if a + pe <=WMM:
            RC = round(pe + w - WM + WM * ((1 - ((pe + a) / WMM))**(b + 1)), 1) + RB
        elif a + pe > WMM:
            RC = round(pe-(WM-w),1) + RB
    return RC
def ThreeR(S_1,pe_1,pe,R,R_1):

    if pe <= 0:
        l = [0,0,0,0]
    else:
        FR = R / pe
        if pe_1 <= 0:
            FR_1 = 0
        else:
            FR_1 = R_1 / pe_1
        au = SMM * (1 - ((1 - ((S_1*FR_1) / (SM*FR))) ** (1 / (1 + EX))))
        if au + pe < SMM:
            RS = FR*(pe + (S_1*FR_1)/FR - SM + SM * ((1 - ((pe + au) / SMM)) ** (EX + 1)))
        elif au + pe >= SMM:
            RS = FR*(pe - (SM - (S_1*FR_1)/FR))
        S = (S_1*FR_1)/FR + (R-RS)/FR
        RI = KI*S*FR
        RG = KG*S*FR
        S_1 = S*(1-KI-KG)
        l = [RS,RI,RG,S_1]
    return l
def QT(Q0,l,Cx):
    QT = [0]*(len(l) + 1)
    QT[0] = Q0
    for i in range(1,len(QT)):
        QT[i] = Cx*QT[i-1] + (1-Cx)*l[i-1]*(553/(3.6*3))
    return QT[1:]

for i in range(len(CT)):
    CT[i][0] = round(all_rows[i][1]*KC,1)
    CT[i][1] = round(all_rows[i][2]*0.33+all_rows[i][3]*0.14+all_rows[i][4]*0.33+all_rows[i][5]*0.20,1)
for i in range(len(CT)):
    if i == 0:
        CT[i][2] = EU(CT[i][7],CT[i][1],CT[i][0])
        CT[i][3] = EL(CT[i][8], CT[i][0], CT[i][2])
        CT[i][4] = ED(CT[i][8], CT[i][0], CT[i][2], CT[i][3])
        CT[i][5] = round(sum(CT[i][2:5]),1)
        CT[i][6] = round(CT[i][1]-CT[i][5],1)
        CT[i][11] = round(RC(CT[i][10],CT[i][6]),1)
        CT[i][12] = round(ThreeR(S0, CT[i-1][6],CT[i][6], CT[i][11], CT[i][11])[0],1)
        CT[i][13] = round(ThreeR(S0, CT[i-1][6],CT[i][6], CT[i][11], CT[i][11])[1],1)
        CT[i][14] = round(ThreeR(S0, CT[i-1][6],CT[i][6], CT[i][11], CT[i][11])[2],1)
        CT[i][15] = round(ThreeR(S0, CT[i-1][6],CT[i][6], CT[i][11], CT[i][11])[3],1)
    else:
        CT[i][7] = WUC(CT[i-1][1], CT[i-1][2], CT[i - 1][7], CT[i - 1][11])
        CT[i][8] = WLC(CT[i-1][1], CT[i-1][2], CT[i-1][3], CT[i - 1][7], CT[i - 1][8], CT[i - 1][11])
        CT[i][9] = WDC(CT[i-1][1], CT[i-1][2], CT[i-1][3], CT[i-1][4], CT[i - 1][7], CT[i - 1][8], CT[i - 1][9],CT[i - 1][11])
        CT[i][10] = round(sum(CT[i][7:10]),1)
        CT[i][2] = EU(CT[i][7],CT[i][1],CT[i][0])
        CT[i][3] = EL(CT[i][8], CT[i][0], CT[i][2])
        CT[i][4] = ED(CT[i][8], CT[i][0], CT[i][2],CT[i][3])
        CT[i][5] = round(sum(CT[i][2:5]),1)
        CT[i][6] = round(CT[i][1] - CT[i][5],1)
        CT[i][11] = round(RC(CT[i][10], CT[i][6]),1)
        CT[i][12] = round(ThreeR(CT[i - 1][15],CT[i-1][6], CT[i][6], CT[i][11], CT[i - 1][11])[0],1)
        CT[i][13] = round(ThreeR(CT[i - 1][15],CT[i-1][6], CT[i][6], CT[i][11], CT[i - 1][11])[1],1)
        CT[i][14] = round(ThreeR(CT[i - 1][15],CT[i-1][6], CT[i][6], CT[i][11], CT[i - 1][11])[2],1)
        CT[i][15] = round(ThreeR(CT[i - 1][15],CT[i-1][6], CT[i][6], CT[i][11], CT[i - 1][11])[3],1)
Rsl = []
Ril = []
Rgl = []
for i in range(len(CT)):
    Rsl.append(CT[i][12])
    Ril.append(CT[i][13])
    Rgl.append(CT[i][14])
Qsl = QT(QS0,Rsl,CS)
Qil = QT(QI0,Ril,CI)
Qgl = QT(QG0,Rgl,CG)
for i in range(len(CT)):
    CT[i][16] = round(Qsl[i],1)
    CT[i][17] = round(Qil[i],1)
    CT[i][18] = round(Qgl[i],1)
    CT[i][19] = CT[i][16]+CT[i][17]+CT[i][18]

for i in range(len(CT)):
    CT[i].append(all_rows[i][0])
excel = pd.DataFrame(CT,columns=['Ep','P(mm)','EU','EL','ED','E','PE','WU','WL','WD','W','R(mm)','Rs(mm)','Ri(mm)','Rg(mm)','S_1','Qs(m³/s)','Qi(m³/s)','Qg(m³/s)','Q(m³/s)','时间'])
path = r'C:\Users\86136\Desktop\HF\CourseDesign\TWoutput.xlsx'
selected_columns = ['时间','P(mm)','Rs(mm)','Ri(mm)','Rg(mm)','R(mm)','Qs(m³/s)','Qi(m³/s)','Qg(m³/s)','Q(m³/s)']
excel_selscted = excel[selected_columns]
excel_selscted.to_excel(path,index=False,engine='openpyxl')
