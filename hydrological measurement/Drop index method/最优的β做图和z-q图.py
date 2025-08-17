import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

plt.rcParams['font.sans-serif'] = ['SimHei']

df = pd.read_excel('_beta_.xlsx')

df['Delta Z'] = df['Zu'] - df['Zl']

def _func(x, a, b, c):
    return a * (x)**b + c

def residual(x, y, a, b, c):
    residuals = np.std((y - _func(x, a, b, c))/_func(x, a, b, c))
    return residuals

def f(beta, flag=0):
    df['q1'] = df['Q'] / (df['Delta Z']**beta)

    # 进行曲线拟合
    params , _ = curve_fit(_func, df['Zu'], df['q1'], maxfev=20000)

    # 提取拟合参数
    a, b, c = params

    if flag:
        # 计算拟合曲线的点（使用Zu作为x坐标）
        x_fit = np.linspace(df['Zu'].min(), df['Zu'].max(), 100)
        y_fit = _func(x_fit, a, b, c)

        # 将拟合曲线的点转换为q1作为x坐标，Zu作为y坐标
        # 这里需要解反函数 x = ( (y-c)/a )^(1/b)
        x_plot = y_fit
        y_plot = ((x_plot - c) / a) ** (1 / b) if b != 0 else np.zeros_like(x_plot)

        # 绘制原始数据点 (q1作为x，Zu作为y)
        plt.plot(df['q1'], df['Zu'], 'o', label='Data')
        # 绘制拟合曲线 (转换后的坐标)
        plt.plot(x_plot, y_plot, '-', label='Fit')

        plt.xlabel('q')
        plt.ylabel('Z')
        plt.legend()
        plt.savefig('_Z-q.jpg', dpi=600)
        plt.show()

    residuals = round(residual(df['Zu'], df['q1'], a, b, c)*100, 2)

    return residuals,a,b,c

def main():
    df_new = pd.DataFrame(columns=['beta', 'error'])

    for i in range(100):
        beta = i / 100
        error, a, b, c = f(beta, 0)  # 调用 f 函数计算误差和拟合参数
        df_new.loc[i] = [beta, error]
        #print(f"beta: {beta}, error: {error}")

    df_new.to_excel('_beta-S.xlsx', index=False)

    df_new.plot(x='error', y='beta')
    plt.xlabel('Standardized residuals (%)')
    plt.ylabel('落差指数  $ \\beta $ ')
    plt.savefig('_beta-S.jpg', dpi=600)
    plt.show()

    min_index = df_new['error'].idxmin()
    min_beta = df_new.loc[min_index, 'beta']

    return f(min_beta, 1)

main()

