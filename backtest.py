"""
回测脚本 - 2025年全年
策略: 无持仓买入，有持仓卖出
"""

import rqdatac as rq
import pandas as pd
import numpy as np
import os

# 从环境变量读取米筐 License
LICENSE_URI = os.environ.get("RQDATAC_URI")
if not LICENSE_URI:
    raise ValueError("请设置环境变量 RQDATAC_URI")

rq.init(uri=LICENSE_URI)

# 回测参数
SYMBOL = "600519.XSHG"  # 茅台
INITIAL_CAPITAL = 100000  # 初始资金10万
POSITION_SIZE = 50  # 每次买入数量

# 获取2025年历史数据
print("获取2025年历史数据...")
df = rq.get_price(SYMBOL, start_date='2025-01-01', end_date='2025-12-31')

# 处理数据格式
df = df.reset_index()
df = df.rename(columns={'order_book_id': 'symbol', 'date': 'date'})
df = df.sort_values('date').reset_index(drop=True)

print(f"数据范围: {df['date'].min()} ~ {df['date'].max()}")
print(f"交易日数: {len(df)}")

# 回测模拟
cash = INITIAL_CAPITAL
position = 0
portfolio_value = []
trade_log = []

for i, row in df.iterrows():
    date = row['date']
    price = row['close']
    
    # 策略逻辑
    if position == 0:
        cost = price * POSITION_SIZE
        if cash >= cost:
            position = POSITION_SIZE
            cash -= cost
            trade_log.append({'date': date, 'action': 'BUY', 'price': price, 'shares': POSITION_SIZE})
    else:
        revenue = price * position
        cash += revenue
        trade_log.append({'date': date, 'action': 'SELL', 'price': price, 'shares': position})
        position = 0
    
    portfolio_val = cash + position * price
    portfolio_value.append({'date': date, 'value': portfolio_val})

portfolio_df = pd.DataFrame(portfolio_value)
trades_df = pd.DataFrame(trade_log)

# 计算指标
final_value = portfolio_df['value'].iloc[-1]
total_return = (final_value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
years = len(df) / 252
annualized_return = ((final_value / INITIAL_CAPITAL) ** (1/years) - 1) * 100

portfolio_df['peak'] = portfolio_df['value'].cummax()
portfolio_df['drawdown'] = (portfolio_df['peak'] - portfolio_df['value']) / portfolio_df['peak'] * 100
max_drawdown = portfolio_df['drawdown'].max()

portfolio_df['daily_return'] = portfolio_df['value'].pct_change()
risk_free_rate = 0.02
daily_rf = risk_free_rate / 252
excess_return = portfolio_df['daily_return'] - daily_rf
sharpe_ratio = np.sqrt(252) * excess_return.mean() / excess_return.std() if excess_return.std() > 0 else 0

# 胜率统计
buy_trades = trades_df[trades_df['action'] == 'BUY']
sell_trades = trades_df[trades_df['action'] == 'SELL']
winning_trades = 0
total_profit = 0
if len(sell_trades) > 0 and len(buy_trades) > 0:
    for i in range(len(sell_trades)):
        buy_price = buy_trades.iloc[i]['price']
        sell_price = sell_trades.iloc[i]['price']
        shares = sell_trades.iloc[i]['shares']
        profit = (sell_price - buy_price) * shares
        total_profit += profit
        if profit > 0:
            winning_trades += 1

win_rate = winning_trades / len(sell_trades) * 100 if len(sell_trades) > 0 else 0

# 输出结果
print("\n" + "="*50)
print("回测结果 - 简单择时策略 (2025全年)")
print("="*50)
print(f"标的: {SYMBOL} (茅台)")
print(f"初始资金: {INITIAL_CAPITAL:,.2f} 元")
print(f"最终资产: {final_value:,.2f} 元")
print("-"*50)
print(f"总收益率: {total_return:.2f}%")
print(f"年化收益率: {annualized_return:.2f}%")
print(f"最大回撤: {max_drawdown:.2f}%")
print(f"夏普比率: {sharpe_ratio:.2f}")
print("-"*50)
print(f"买入次数: {len(buy_trades)}")
print(f"卖出次数: {len(sell_trades)}")
print(f"胜率: {win_rate:.1f}%")
print(f"总盈利: {total_profit:,.2f} 元")
print("="*50)

# 保存结果
portfolio_df.to_csv('backtest_result.csv', index=False)
print("\n组合曲线已保存到 backtest_result.csv")
