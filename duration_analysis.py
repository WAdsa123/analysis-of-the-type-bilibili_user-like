import pandas as pd
import matplotlib.pyplot as plt
import lightgbm as lgb
import seaborn as sns
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
df1 = pd.read_excel('F:\\work_code\\bili_weekly_tag.xlsx')
df2 = pd.read_excel('F:\\work_code\\video_date.xlsx')
comfortable_time=df1[['video_tname','video_views','video_duration','Bvid']]
df = pd.merge(comfortable_time, df2, on='Bvid').drop(['Unnamed: 0.1', 'Unnamed: 0','Bvid'], axis=1)
df['ctime'] = pd.to_datetime(df['ctime'], unit='s') + pd.Timedelta(hours=8)
df['year'] = df['ctime'].dt.year
df['quarter'] = df['ctime'].dt.quarter
df['month'] = df['publish_time'].dt.to_period('M')
def length_group(x):
    if x < 60:
        return '<1m'
    elif 60 <= x < 180:
        return '1-3m'
    elif 180 <= x < 300:
        return '3-5m'
    else:
        return '>5m'
df['length_group'] = df['video_duration'].apply(length_group)
agg_df = df.groupby(['year', 'length_group'])['video_views'].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 6))
for group in agg_df['length_group'].unique():
    temp = agg_df[agg_df['length_group'] == group]
    ax.plot(temp['year'], temp['video_views'], marker='o', label=group)
ax.set_xlabel('年份')
ax.set_ylabel('平均播放量')
ax.set_title('2019-2025年不同长度视频的平均播放量变化')
ax.set_xticks(range(2019, 2026))  # 固定x轴为2019-2025
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
pivot_df = agg_df.pivot(index='length_group', columns='year', values='video_views')
plt.figure(figsize=(10, 4))
sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap='YlGnBu')
plt.title('2019-2025年不同长度视频播放量热力图')
plt.tight_layout()
plt.show()




df['year'] = df['year'].astype(int)
df['length_year_interact'] = df['video_duration'] * df['year']
df['length_quarter_interact'] = df['video_duration'] * df['quarter']
features = ['video_duration', 'year', 'quarter', 'length_year_interact', 'length_quarter_interact']
X = df[features]
y = df['video_views']
train_df = df[df['year'] <= 2024]
test_df = df[df['year'] == 2025]
X_train, y_train = train_df[features], train_df['video_views']
X_test, y_test = test_df[features], test_df['video_views']
model = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    verbose=-1
)

early_stopping = lgb.early_stopping(
    stopping_rounds=10,
    verbose=False
)
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    callbacks=[early_stopping]
)
lgb.plot_importance(model, importance_type='gain', title='特征重要性（Gain）')
plt.tight_layout()
plt.show()


def plot_custom_pdp(model, X_data, feature_name, target_years, grid_points=50):
    feature_min = X_data[feature_name].min()
    feature_max = X_data[feature_name].max()
    feature_grid = np.linspace(feature_min, feature_max, grid_points)
    fig, ax = plt.subplots(figsize=(12, 7))
    for year in target_years:
        X_pdp = X_data.copy()
        X_pdp['year'] = year
        X_pdp['quarter'] = 2
        X_pdp['length_year_interact'] = X_pdp[feature_name] * X_pdp['year']
        X_pdp['length_quarter_interact'] = X_pdp[feature_name] * X_pdp['quarter']
        pdp_values = []
        for val in feature_grid:
            X_temp = X_pdp.copy()
            X_temp[feature_name] = val
            pred = model.predict(X_temp)
            pdp_values.append(np.mean(pred))
        ax.plot(feature_grid, pdp_values, label=f'{year}年', linewidth=2, marker='.')
    ax.set_xlabel(f'{feature_name}（秒）', fontsize=12)
    ax.set_ylabel('平均预测播放量', fontsize=12)
    ax.set_title('不同年份下视频长度对播放量的部分依赖关系（手动实现）', fontsize=14)
    ax.legend(loc='best')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
plot_custom_pdp(model, X_test, 'video_duration', target_years=[2020, 2023, 2025])
def length_bin(x):
    if x < 60:
        return '<1分钟'
    elif 60 <= x < 180:
        return '1-3分钟'
    elif 180 <= x < 300:
        return '3-5分钟'
    else:
        return '>5分钟'
test_df['length_bin'] = test_df['video_duration'].apply(length_bin)
test_df['pred_play_count'] = model.predict(test_df[features])
group_pred = test_df.groupby(['year', 'length_bin'])['pred_play_count'].mean().reset_index()
plt.figure(figsize=(12, 6))
sns.barplot(data=group_pred, x='year', y='pred_play_count', hue='length_bin')
plt.xlabel('年份', fontsize=12)
plt.ylabel('平均预测播放量', fontsize=12)
plt.title('各年份不同长度区间视频的平均预测播放量', fontsize=14)
plt.legend(loc='best')
plt.tight_layout()
plt.show()