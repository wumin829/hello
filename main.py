"""
简单下单策略 - 接入米筐实时行情
- 无持仓 -> 买入
- 有持仓 -> 卖出
"""

import rqdatac as rq
import os

# 从环境变量读取米筐 License
LICENSE_URI = os.environ.get("RQDATAC_URI")
if not LICENSE_URI:
    raise ValueError("请设置环境变量 RQDATAC_URI")

# 初始化rqdatac
rq.init(uri=LICENSE_URI)

# 模拟持仓数据（实际从券商API获取）
positions = {}  # {symbol: quantity}


def get_current_price(symbol: str) -> float:
    """
    获取当前价格（从米筐API）
    symbol格式: 600519.XSHG (上海), 000001.XSHE (深圳)
    """
    # 转换代码格式
    if symbol.isdigit():
        if symbol.startswith('6'):
            symbol = f"{symbol}.XSHG"
        else:
            symbol = f"{symbol}.XSHE"
    
    # 获取最新行情
    df = rq.get_price(symbol, start_date='2026-03-01', end_date='2026-03-10')
    if df is not None and not df.empty:
        return float(df['close'].iloc[-1])
    raise ValueError(f"无法获取 {symbol} 的行情数据")


def get_position(symbol: str) -> int:
    """获取持仓数量"""
    # 实际项目中从券商API或数据库获取
    return positions.get(symbol, 0)


def buy(symbol: str, quantity: int = 100):
    """买入"""
    price = get_current_price(symbol)
    cost = price * quantity
    print(f"[买入] {symbol} x{quantity} @ {price:.2f} (总额: {cost:.2f})")
    # 实际项目中调用券商API下单
    positions[symbol] = positions.get(symbol, 0) + quantity


def sell(symbol: str, quantity: int = None):
    """卖出"""
    current_qty = get_position(symbol)
    if quantity is None:
        quantity = current_qty
    
    price = get_current_price(symbol)
    revenue = price * quantity
    print(f"[卖出] {symbol} x{quantity} @ {price:.2f} (总额: {revenue:.2f})")
    # 实际项目中调用券商API下单
    positions[symbol] = max(0, positions.get(symbol, 0) - quantity)


def run_strategy(symbol: str):
    """执行策略"""
    current_qty = get_position(symbol)
    
    print(f"\n标的: {symbol}, 当前持仓: {current_qty}")
    
    if current_qty == 0:
        print("策略: 无持仓 -> 买入")
        buy(symbol, 100)
    else:
        print("策略: 有持仓 -> 卖出")
        sell(symbol)
    
    print(f"执行后持仓: {get_position(symbol)}")


if __name__ == "__main__":
    # 测试 - 茅台
    run_strategy("600519")
