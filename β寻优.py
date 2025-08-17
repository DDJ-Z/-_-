import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.rcParams['font.sans-serif'] = ['SimSun']

df = pd.read_excel('_beta_.xlsx')


df['Delta Z'] = df['Zu'] - df['Zl']

def _func(x, a, b, c):
    return a * (x)**b + c#定义函数

def residual(x, y, a, b, c):
    residuals = np.std((y - _func(x, a, b, c))/_func(x, a, b, c))#计算残差的标准差
    return residuals

def f(beta, flag=0):
    df['q'] = df['Q'] / (df['Delta Z']**beta)

    # 进行曲线拟合
    params, _ = curve_fit(_func, df['Zu'], df['q'],  maxfev=100000)#迭代100000次

    # 提取拟合参数
    a, b, c = params

    if flag:
        # 创建拟合曲线
        x = np.linspace(df['Zu'].min(), df['Zu'].max(), 100)
        y_fit = _func(x, a, b, c)

        # 绘制原始数据和拟合曲线
        plt.plot(df['q'], df['Zu'], 'o', label='Data')
        plt.plot(y_fit, x, '-', label='Fit')
        plt.xlabel('q')
        plt.ylabel('Z')
        plt.legend()
        plt.savefig('Z-q.jpg', dpi=600)
        plt.show()
    residuals = residual(df['Zu'], df['q'], a, b, c) * 100#残差标准差计算
    return residuals,a,b,c

def bisection(a, b, tol=6):
    """
    a: 区间左端点
    b: 区间右端点
    tol: 容差
    """
    for i in range(tol):
        d = 10 ** (-1 - i)
        while True:
            f1 = f(a + d)[0]
            f2 = f(a + 2 * d)[0]
            if f1 > f2:
                a = a + d
            else:
                break

    return a#残值标准差最小值对应的beta

beta_best = bisection(0, 1)
print("β = ",beta_best)
error,a,b,c = f(beta_best, 0)
print("误差:",error,"\n","a = ",a,"\n","b = ",b,"\n","c = ",c)#最优的beta对应的残值标准差



