import pandas as pd

class KC:
    def __init__(self,filepath,KC_0,time,WU0,WL0,WD0):
        self.filepath = pd.read_csv(filepath,encoding='gbk')
        self.KC_0 = KC_0
        self.time = time
        self.WU0 = WU0
        self.WL0 = WL0
        self.WD0 = WD0
    def KCCalculate(self):
        all_rows = self.filepath.values.tolist()
        '''all_rows第零行为例子,数据含义是all_rows[0][0]是时间,all_rows[0][1]是实测径流,all_rows[0][2]是E0, 3,4,5,6是P1,P2,P3,P4'''
        CT = [[0] * 12 for i in range(len(all_rows))]
        '''第零行为例子,CT[0][0]是Ep,CT[0][1]是P,2是EU,3是EL,4是ED,5是E,6是PE,7是WU,8是WL,9是WD,10是W,11是R总'''
        WUM=20
        WLM=70
        WDM=50
        C=0.16
        b=0.2
        IM=0.001
        WM=WUM+WLM+WDM
        WMM=(1+b)*WM/(1-IM)
        F = 553 #平方千米
        R_a = sum(all_rows[i][1] for i in range(len(all_rows)))*((24*3600)/(F*1000)) #mm
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
            RB = pe * IM  # RB是不透水区域产流
            if pe <= 0:
                RC = round(0,1)
            else:
                a = WMM * (1 - ((1 - (w / WM))**(1/(1 + b))))
                if a + pe <=WMM:
                    RC = round(pe + w - WM + WM * ((1 - ((pe + a) / WMM))**(b + 1)), 1) + RB
                elif a + pe > WMM:
                    RC = round(pe-(WM-w),1) + RB
            return RC
        CT[0][7] = self.WU0
        CT[0][8] = self.WL0
        CT[0][9] = self.WD0
        CT[0][10] = CT[0][7]+CT[0][8]+CT[0][9]
        KC = self.KC_0
        for i in range(len(CT)):
            CT[i][0] = round(all_rows[i][2]*KC,1)
            CT[i][1] = round(all_rows[i][3]*0.33+all_rows[i][4]*0.14+all_rows[i][5]*0.33+all_rows[i][6]*0.20,1)
        for i in range(len(CT)):
            if i == 0:
                CT[i][2] = EU(CT[i][7],CT[i][1],CT[i][0])
                CT[i][3] = EL(CT[i][8], CT[i][0], CT[i][2])
                CT[i][4] = ED(CT[i][8], CT[i][0], CT[i][2], CT[i][3])
                CT[i][5] = round(sum(CT[i][2:5]),1)
                CT[i][6] = round(CT[i][1]-CT[i][5],1)
                CT[i][11] = RC(CT[i][10],CT[i][6])
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
                CT[i][11] = RC(CT[i][10], CT[i][6])
        R_c = sum(CT[i][11] for i in range(len(CT)))
        AError = R_c - R_a
        RError = AError/R_a
        loutput = [self.time,round(R_a,1),round(R_c,1),round(AError,1),round(RError*100,1),KC]
        xop = [CT[-1][7],CT[-1][8],CT[-1][9]]
        LX=[loutput,xop]
        return LX
filepath_1 = r'C:\Users\86136\Desktop\HF\CourseDesign\data\1990.csv'
filepath_2 = r'C:\Users\86136\Desktop\HF\CourseDesign\data\1991.csv'
control = True
n = 0
KC0 = 0.9
while control:
    step = 0.01
    K = KC0 + n*step
    KC_1991 = KC(filepath_1, K,1991,20,70,50).KCCalculate()
    KC_1992 = KC(filepath_2, K,1992,KC_1991[1][0],KC_1991[1][1],KC_1991[1][2],).KCCalculate()
    if abs(KC_1991[0][4]) <= 5 and abs(KC_1992[0][4]) <= 5:
        control = False
    else:
        n += 1
print(KC_1991,KC_1992)
CSOutput_1 = [KC_1991[0],KC_1992[0]]
excel = pd.DataFrame(CSOutput_1,columns=['年份','实测R(mm)','计算R(mm)','绝对误差(mm)','相对误差(%)','KC'])
path = r'C:\Users\86136\Desktop\HF\CourseDesign\KCoutput.xlsx'
excel.to_excel(path,index=False,engine='openpyxl')
















