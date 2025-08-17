import pandas as pd

def _func(x, a, b, c):
    return a * (x)**b + c

df = pd.read_excel('推流计算.xlsx')
df['Delta Z'] = df['Zu'] - df['Zl']
beta = 0.26780
a = 0.0013293532981284895
b = 5.163879044881668
c = -2298.521988416742
df['q'] = df['Q'] / (df['Delta Z']**beta)

def format_Q(num):
    if num >= 100:
        return int(float('{:.3g}'.format(num)))  # 取 3 位有效数字
    elif num >= 10:
        return format(num, '.1f')  # 取一位小数
    else:
        return format(num, '.2f')  # 取两位小数

# 计算 Qc 列
df['Qc'] = 0.0
for i, row in df.iterrows():
    df.at[i, 'Qc'] = format_Q(_func(row['Zu'], a, b, c) * row['Delta Z']**beta)

df.to_excel('_beta_out.xlsx', index=False)