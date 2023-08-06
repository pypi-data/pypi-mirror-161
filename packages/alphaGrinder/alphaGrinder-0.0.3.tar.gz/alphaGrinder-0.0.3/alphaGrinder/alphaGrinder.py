###################################################
##############   A股因子库构建	##################
###################################################

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn import linear_model
from scipy.stats import rankdata
import statsmodels.api as sm
from scipy.linalg import inv
from tqdm import tqdm
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
import warnings
warnings.filterwarnings("ignore")


#### 所有因子背后的基础数据均来源于本地整理过后的Wind原始数据库
#### 主要基础数据包括：
#### 1. 证券基础信息（包括证券代码表——"WINDCUSTOMCODE"、行业分类表——INDUSTRIES）
#### 2. 股票日频交易信息表（tbl_trading, tbl_amt, 以及其每年对应的数据）
#### 3. 财务报表信（tbl_balance, tbl_fa）
#### 4. 分析师预期信息
db = create_engine('postgresql+psycopg2://postgres:123456@localhost/postgres')
db.connect()



###################################################
##############   辅助功能函数集合 ##################
###################################################

#### 获取常规财务指标

def get_stocks(start_day, end_day):
	""" 生成常用股票池 """
	query = """ SELECT "日期","证券ID","[内部]交易状态代码"
				FROM "tbl_amt"
				WHERE "日期" >= '{}' 
				AND   "日期" <= '{}' """.format(start_day, end_day)
	stocks = pd.read_sql(query, con=db)

	
	stocks['日期'] = pd.to_datetime( stocks['日期'])
	stocks.sort_values('日期',inplace=True)
	# stocks_universe = \
	# stocks.groupby([stocks['证券ID'], stocks['日期'].dt.year, stocks['日期'].dt.month]).tail(1)

	# 每月最后一个交易日
	trade_dates = stocks[['日期']].drop_duplicates().sort_values('日期')
	trade_dates =\
	trade_dates.groupby([trade_dates['日期'].dt.year,
						 trade_dates['日期'].dt.month]).tail(1)
	stocks = \
	stocks.merge(trade_dates, on=['日期'],how='inner')

	# 保留当天非停牌股票
	stocks = stocks.loc[stocks['[内部]交易状态代码'] == -1]
	return stocks

def get_report_metrics(stocks,
	source_table,
	metric_name ='' ,
	earlist_report = '2015-01-01',
	db = db,
	left_date_col = '报告期',
	right_date_col= '截止日期',
	report_type = '合并报表'):
	"""计算在各个调仓日，股票池中个股对应的最新财报披露数据"""

	# 以资产负债表的发布时间为标准关联计算因子日期与财报发布日
	date_link = link_report(stocks, earlist_report)
	
	# 获取指标原始值
	db.execute(""" drop table if exists "date_link_tmp" """)
	date_link.to_sql("date_link_tmp", index=False, con=db)
	query = """ SELECT t1.*,
	t2."{}"
	FROM "date_link_tmp" t1
	LEFT JOIN
	"{}" t2
	ON t1."{}" = t2."{}"
	AND t1."公司ID" = t2."公司ID"
	AND t2."报表类型" = '{}'
	""".format(metric_name, source_table,
	           left_date_col, right_date_col,
	           report_type)
	
	data = pd.read_sql(query, con=db)
	db.execute(""" drop table if exists "date_link_tmp" """)
	return data

def SUE(stocks):
	"""计算在各个调仓日，股票池中个股对应的SUE
		SUE计算方法：
		 (最新季度实际单季度净利润 - （去年同期单季度净利润 + 平均单季度净利润同比增量(通过过去八个季度计算)） ) / (单季度净利润同比变化量的标准差（通过过去八个季度计算）)
	"""
	# 统计对应日期的最新报告期
	db.execute("""drop table if exists "tmp"; """)
	code_info = pd.read_sql("WINDCUSTOMCODE",con=db)
	link_report(stocks, earlist_report = '2015-01-01').to_sql("tmp",con=db, index=False)
	db.execute("""alter table "tmp" alter column "报告期" type date using("报告期"::date); """)
	db.execute("""alter table "tmp" alter column "公告日期" type date using("公告日期"::date); """)
	
	# 统计过去三年单季度净利润
	metric_name = '单季度.扣除非经常损益后的净利润' 
	query = """ SELECT t1."日期",
	t1."公司ID",
	t1."证券ID",
	t2."报告期",
	t2."{}"
	FROM "tmp" t1
	join "tbl_fa" t2
	on t1."公司ID" = t2."公司ID"
	where extract(year from t1."报告期") <= extract(year from t2."报告期") + 3
	and t2."报告期" <= t1."报告期"
	and t2."报表类型" = '合并报表' """.format(metric_name)

	earnings_by_quarter = pd.read_sql(query, con = db)
	earnings_by_quarter['quarter_shift'] = \
	earnings_by_quarter.groupby(['日期','证券ID'])['报告期'].transform(lambda x: len(x) - rankdata(x))

	earnings_by_quarter.groupby(['日期','证券ID'])['quarter_shift'].max().to_frame('max_shift')\
	.query("""max_shift >= 12 """)

	df = \
	earnings_by_quarter.set_index(['日期','公司ID','证券ID','quarter_shift']).sort_index()[metric_name].unstack()

	# 确保过去12个季度的数据完整
	df['valid'] = (df.iloc[:,:12].isna().sum(axis=1) == 0)

	sue = pd.DataFrame([], index = df.index)
	sue['recent_quarter_earning'] = df.iloc[:,0]
	sue['past_quarter_earning']   = df.iloc[:,4]

	# 平均单季度同比变化量
	sue['avg_change'] = \
	df.iloc[:,:12].transpose().sort_index(ascending=False).diff(periods = 4).sort_index().transpose()\
	.iloc[:,:8].mean(axis=1).mul(df['valid'])

	sue['expected_earning'] = sue['past_quarter_earning'] + sue['avg_change']

	# 单季度同比变化量的标准差（过去8个季度）
	sue['std'] = \
	df.iloc[:,:12].transpose().sort_index(ascending=False).diff(periods = 4).sort_index().transpose()\
	.iloc[:,:8].std(axis=1).mul(df['valid'])
	sue['SUE'] = (sue['recent_quarter_earning'] - sue['expected_earning']) / sue['std']	
	
	return sue[['SUE']].reset_index()

def link_report(stocks, earlist_report):
	"""
		通过资产负债表的公告日期，关联股票的最新报告公开日
	"""
	query = """ SELECT "报告期", "公告日期", "公司ID" FROM "tbl_balance" where "报告期" >= '{}'
				AND "报表类型" = '合并报表' """.format(earlist_report)
	report_dates = pd.read_sql(query, con = db)
	
	query = """ SELECT * FROM "WINDCUSTOMCODE" """
	code_info = pd.read_sql(query, con = db)
	
	df1 = stocks.merge(code_info[['证券ID','公司ID']], on=['证券ID'], how='left')
	df2 = report_dates
	df1['year'] = df1['日期'].dt.year
	df1['year_before'] = df1['日期'].dt.year - 1
	df2['报告期'] = pd.to_datetime(df2['报告期'])
	df2['公告日期'] = pd.to_datetime(df2['公告日期'])
	df2['year'] = df2['公告日期'].dt.year
	tmp = pd.concat([df1.merge(df2, on=['公司ID','year']).sort_values(['公告日期','报告期']).query(""" 公告日期 < 日期 """),
					 df1.merge(df2,
							   left_on=['公司ID','year_before'],
							   right_on = ['公司ID','year']).sort_values(['公告日期','报告期']).query(""" 公告日期 < 日期 """)])
	tmp.sort_values(['公告日期','报告期'],inplace = True)
	date_link = tmp.groupby(['公司ID','日期']).tail(1)[['日期','证券ID','公司ID','报告期','公告日期']]  
	return date_link

def roe_metrics(stocks, calc_type = 'ROE', source_table = 'tbl_fa', report_type = '合并报表'):
	 """ 计算 ROE (DELTA_ROE) 或者 ROA (DELTA_ROA)"""
	 if calc_type == 'ROE':
		 metric_name = '单季度.净资产收益率(扣除非经常损益)'
	 elif calc_type == 'ROA':
		 metric_name = '单季度.总资产净利润'
	 else:
		 print("无效的财务比率类型")
		 return 

	 data = \
	 get_report_metrics(stocks,
						metric_name=metric_name,
						source_table=source_table,
						left_date_col = '报告期',
						right_date_col = '报告期',
						report_type = report_type)   

	 delta_ = data[['证券ID','报告期',metric_name]].drop_duplicates()
	 delta_['quarter'] = delta_['报告期'].dt.month
	 delta_.sort_values(['证券ID','报告期'],inplace=True)
	 delta_['DELTA'] = delta_.groupby(['证券ID','quarter'])[[metric_name]].diff()

	 data = data.merge(delta_[['证券ID','报告期','DELTA']],
					   on=['证券ID','报告期'], how='left')	
	 data.rename(columns = {'DELTA':'DELTA_'+calc_type},inplace=True)
	 return data

#### 获取 动量/反转/流动性指标
def get_turnover(start_day, N = 20):
    """获取过去N日平均换手率"""
    query = """ select
                t1."证券ID",
                t1."日期",
                avg("换手率(%)") over (partition by "证券ID" order by t1."日期" ROWS BETWEEN
                {} PRECEDING AND CURRENT ROW) as turnover_{}d
                from tbl_trading t1
                where t1."日期" >= '{}'
                """.format(N-1, N, start_day)
    turnover = pd.read_sql(query, con=db)
    turnover['日期'] = pd.to_datetime(turnover['日期'])  
    return turnover

def get_atr(start_day, N = 20):
    """获取过去N日真实日内波动率"""
    query = \
    """select 
        t."日期",
        t."证券ID",
        avg(t."TR") over (partition by "证券ID" order by t."日期" ROWS BETWEEN
                    {} PRECEDING AND CURRENT ROW) as ATR_{}D
        from(
        select 
        "日期",
        "证券ID",
        greatest(abs("最高价" - "最低价")/"最低价",
                 abs("昨收盘价" - "最高价")/"最高价",
                 abs("昨收盘价" - "最低价")/"最低价") as "TR"
        from tbl_amt
        WHERE "日期" >= '{}') t;""".format(N-1, N, start_day)
    atr = pd.read_sql(query, con=db)
    atr['日期'] = pd.to_datetime(atr['日期'])  
    return atr

def get_momentum(start_day, N = 60):
    """计算过去N日涨跌幅"""
    try:
        return_past =  pd.read_sql(""" SELECT * FROM return_{}d WHERE "日期" >= '{}' """.format(N, start_day),
                                  con = db)
    except:
        print('重新计算过去{}日个股涨跌幅（反转指标）'.format(N))
        query = """ create table return_{}d
                    as(
                    select 
                    t2."日期",
                    t2."证券ID",
                    exp(t2.log_factor) - 1 as return_{}d
                    from
                    (select
                    t1."证券ID",
                    t1."日期",
                    sum(ln(1+t1."涨跌幅(%)"/100)) over (partition by "证券ID" order by t1."日期" ROWS BETWEEN
                    {} PRECEDING AND CURRENT ROW) as log_factor
                    from tbl_trading t1
                    where t1."日期" >= '{}'
                    ) t2)
                    """.format(N, N, N-1, start_day)
        db.execute(sqlalchemy.text(query))
        return_past =  pd.read_sql(""" SELECT * FROM return_{}d WHERE "日期" >= {} """.format(N, start_day),
                                   con = db)
    return return_past