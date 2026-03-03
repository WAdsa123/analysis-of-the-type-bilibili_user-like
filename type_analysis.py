import pandas as pd
import numpy as np
import operator
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.seasonal import STL

plt.rcParams['font.sans-serif'] = ['STHeiti']
df1 = pd.read_excel('/Users/Zhuanz/Documents/副本video_date.xlsx')
df2 = pd.read_excel('/Users/Zhuanz/Documents/bili_weekly_tag.xlsx')
df = pd.merge(df1,df2,on = 'Bvid',how='right')
df['ctime']= pd.to_datetime(df['ctime'], unit='s')+pd.Timedelta(hours=8)
df = df.drop(columns=['Unnamed: 0.1_x','Unnamed: 0_x','Unnamed: 0.1_y','Unnamed: 0_y'],axis=1)
print(df.columns)
'''def tag_pre_process(df:pd.DataFrame):
    
    
    culture_condition=['搞笑','小剧场','明星','游戏','影视','动漫','MAD','电台','音乐','翻唱','手书','同人','舞蹈','搞笑']
    dailylife_condition=['汪','喵','宠','日常','美食']
    new_condition=['手工','DIY','设计',]
    society_condition=['社科','财经','热点']
    vellege_condition=['三农','田园']
    c_m_c = df['video_tname'].str.contains('|'.join(culture_condition), na=False)
    d_m_c = df['video_tname'].str.contains('|'.join(dailylife_condition), na=False)
    n_m_c = df['video_tname'].str.contains('|'.join(new_condition), na=False)
    s_m_c = df['video_tname'].str.contains('|'.join(society_condition), na=False)
    df.loc[c_m_c, 'video_tname'] = '文娱'
    df.loc[d_m_c,'video_tname'] = '日常'
    df.loc[n_m_c,'video_tanem'] = '创新'
    df.loc[s_m_c,'video_tname'] = '社会'
    test_df=df[['video_tname']]
    print(test_df[~test_df['video_tname'].isin(['文娱','日常','创新','社会'])])
'''
def pre_process_show_mainly_year_month_head_video(df:pd.DataFrame):
    figure_df = pd.DataFrame({})
    df['year']= pd.to_datetime(df['ctime']).dt.year.astype(str)
    df['month']= df['ctime'].dt.to_period('M').astype(str)
    df = df.groupby(["month","video_tname"]).agg(
        total_views=('video_views', 'sum'),
        total_video=('video_tname', 'count')
    ).reset_index()

    for i in range(0,len(df['month'].drop_duplicates())-1):
        month=df['month'].drop_duplicates().iat[i]

        figure_df = pd.concat([figure_df,df[df['month']==month].head()],axis=0)
    return figure_df
    '''df_2019 = df[df['year']=='2019.0'].sort_values(by='total_views',ascending=False)
    df_2020 = df[df['year']=='2020.0'].sort_values(by='total_views',ascending=False)
    df_2021 = df[df['year']=='2021.0'].sort_values(by='total_views',ascending=False)
    df_2022 = df[df['year']=='2022.0'].sort_values(by='total_views',ascending=False)
    df_2023 = df[df['year']=='2023.0'].sort_values(by='total_views',ascending=False)
    df_2024 = df[df['year']=='2024.0'].sort_values(by='total_views',ascending=False)
    df_2025 = df[df['year']=='2025.0'].sort_values(by='total_views',ascending=False)
    print(df_2019.head())
    print(df_2020.head())
    print(df_2021.head())
    print(df_2022.head())
    print(df_2023.head())
    print(df_2024.head())
    print(df_2025.head())'''
def show_mainly_year_month_head_video(df:pd.DataFrame,target_tname):
    target_data= df[df['video_tname']==target_tname]

    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(
        target_data['month'],
        target_data['total_views'],
        color='blue',
        linewidth=2,
        marker='o',
        markersize=5,
        markerfacecolor='red',
        alpha=0.5,
    )
    ax.fill_between(
        target_data['month'],
        target_data['total_views'],
        color='blue',
        alpha=0.2,
    )
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)
    ax.set_title(
        f"{target_tname}--月度播放量变化",
        fontsize=10,
        fontweight='bold',
        color='black'
    )
    ax.set_xlabel("time",fontsize=10, fontweight='bold',color='black')
    ax.set_ylabel("views",fontsize=10, fontweight='bold',color='black')
    ax.grid(True)
    plt.tight_layout()
    plt.show()

'''
while True:
    print("输入0退出绘图，输入1开始或继续绘图")
    state = input()
    if state == '0' :
        break
    if state == '1' :
        print("输入目标变量")
        target_tname = input().strip()
        show_mainly_year_month_head_video(views_df,target_tname)
'''
'''基于时序分析的用户生态分析'''
def pre_process_time_analysis(df:pd.DataFrame,target_tname):
    min_date = df['ctime'].min()
    df['week_num']= (df['ctime']-min_date).dt.days//7+1
    df3 = df.groupby(['ctime', 'video_tname']).agg(
        video_views=('video_views', 'sum')
    ).reset_index()
    df = df.groupby(['week_num','video_tname']).agg(
        video_views=('video_views', 'sum'),
        video_count=('video_tname', 'count')
    ).reset_index()
    df3 =df3[df3['video_tname']==target_tname]
    df['views_ratio'] = df.groupby('week_num')['video_views'].transform(lambda x: x / x.sum())
    df['num_ratio'] = df.groupby('week_num')['video_count'].transform(lambda x: x / x.sum())
    df1=df[df['video_tname']==target_tname]
    views_df = pd.DataFrame({
        'week_num': df1['week_num'],
        f'{target_tname}': df1['views_ratio'],
    })
    counts_df = pd.DataFrame({
        'week_num': df1['week_num'],
        f'{target_tname}': df1['num_ratio'],
    })
    stl_df = pd.DataFrame({
        'ctime': df['week_num'],
        f'{target_tname}': df['views_ratio']
    })
    stl_df = stl_df.set_index('ctime')
    return df,views_df,counts_df,stl_df
def rolling_average_variance_extremum(df:pd.DataFrame,target_tname):
    windows = [4,12]
    for win in windows:
        df[f'roll_mean_{win}'] = df[[target_tname]].rolling(window=win,center=True).mean()
        df[f'roll_var_{win}'] = df[[target_tname]].rolling(window=win,center=True).var()
        df[f'roll_max_{win}'] = df[[target_tname]].rolling(window=win).max()
        plt.figure(figsize=(12,6))
        plt.plot(
            df['week_num'],
            df[f'roll_mean_{win}'],
            label= f'{win}周均值',
            color='blue',
            linewidth=2,
            marker='o',
            markersize=5,
        )
        plt.title(f'每周必看中{target_tname}趋势变化',fontsize=10,pad=20)
        plt.xlabel('每周看期数',fontsize=10, fontweight='bold',color='black')
        plt.ylabel('占比（%）',fontsize=10, fontweight='bold',color='black')
        plt.grid(True)
        plt.show()
def STL_tred_season_resid(df:pd.DataFrame):
    arr=df.columns
    stl = STL(df,period=12,robust=True)
    result = stl.fit()
    trend=result.trend
    seasonal=result.seasonal
    resid=result.resid
    fig,(ax1,ax2,ax3,ax4)=plt.subplots(4,1,figsize=(12,6),sharex=True)
    ax1.plot(
        df,
        color='blue',
        linestyle='dashed',
        linewidth=2,
        marker='o',
        markersize=5
    )
    ax1.set_title(
        f'原始时序{arr[0]}占比（%）',
        fontsize=10,
        fontweight='bold',
        color='black',
        pad=20
    )
    ax1.grid(True)
    ax2.plot(
        trend,
        color='blue',
        linestyle='dashed',
        linewidth=2,
    )
    ax2.set_title(
        f'{arr[0]}长期趋势',
        fontsize=10,
        fontweight='bold',
        color='black',
        pad=20
    )
    ax2.grid(True)
    ax3.plot(
        seasonal,
        color='blue',
        linestyle='dashed',
        linewidth=2,
        marker='o',
        markersize=5
    )
    ax3.set_title(
        f'{arr[0]}季节性变化'
        ,fontsize=10,
        fontweight='bold',
        color='black',
        pad=20
    )
    ax3.grid(True)
    ax4.plot(
        resid,
        color='blue',
        linestyle='dashed',
        linewidth=2,
        marker='o',
        markersize=5
    )
    ax4.set_title(
        f'{arr[0]}残差波动',
        fontsize=10,
        fontweight='bold',
        color='black',
        pad=20
    )
    ax4.grid(True)
    plt.tight_layout()
    plt.show()
target_name = '搞笑'
df1,df2,df3,df4 = pre_process_time_analysis(df,target_name)
STL_tred_season_resid(df4)
'''预测未来视频类型变化'''
