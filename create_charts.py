#!/usr/bin/env python3
"""
生成大多伦多地产新闻图表
需要安装：pip install matplotlib pandas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# 设置中文字体（如果需要）
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据
data = {
    '月份': ['2025年1月', '2026年1月'],
    '平均房价(万加元)': [104.1, 97.3],
    '销售量': [3820, 3082]
}

df = pd.DataFrame(data)

# 创建图表1：房价对比
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 房价柱状图
bars1 = ax1.bar(df['月份'], df['平均房价(万加元)'], color=['#4CAF50', '#F44336'])
ax1.set_title('GTA平均房价对比', fontsize=14, fontweight='bold')
ax1.set_ylabel('万加元', fontsize=12)
ax1.set_ylim(90, 110)

# 在柱子上添加数值
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{height}万', ha='center', va='bottom', fontweight='bold')

# 销售量柱状图
bars2 = ax2.bar(df['月份'], df['销售量'], color=['#2196F3', '#FF9800'])
ax2.set_title('GTA房屋销售量对比', fontsize=14, fontweight='bold')
ax2.set_ylabel('套数', fontsize=12)
ax2.set_ylim(2500, 4000)

# 在柱子上添加数值
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
             f'{height:,}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('gta_price_sales_chart.png', dpi=300, bbox_inches='tight')
print("图表1已保存: gta_price_sales_chart.png")

# 创建图表2：房产类型价格
fig2, ax3 = plt.subplots(figsize=(8, 6))

property_types = ['独立屋', '公寓']
prices = [127.8, 60.5]  # 万加元
changes = [-7.4, -9.8]  # 百分比

bars3 = ax3.bar(property_types, prices, color=['#9C27B0', '#00BCD4'])
ax3.set_title('不同类型房产平均价格', fontsize=14, fontweight='bold')
ax3.set_ylabel('万加元', fontsize=12)
ax3.set_ylim(0, 140)

# 在柱子上添加价格和变化率
for i, (bar, change) in enumerate(zip(bars3, changes)):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{height}万\n({change}%)', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('gta_property_types_chart.png', dpi=300, bbox_inches='tight')
print("图表2已保存: gta_property_types_chart.png")

# 创建图表3：价格趋势
fig3, ax4 = plt.subplots(figsize=(10, 6))

timeline = ['2022年2月峰值', '2026年1月']
values = [133.3, 97.3]  # 万加元
colors = ['#FF5722', '#3F51B5']

bars4 = ax4.bar(timeline, values, color=colors)
ax4.set_title('GTA房价变化趋势 (2022-2026)', fontsize=14, fontweight='bold')
ax4.set_ylabel('万加元', fontsize=12)
ax4.set_ylim(0, 150)

# 计算并显示跌幅
for i, (bar, value) in enumerate(zip(bars4, values)):
    height = bar.get_height()
    if i == 1:  # 第二个柱子显示跌幅
        drop = ((133.3 - 97.3) / 133.3) * 100
        ax4.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{height}万\n(较峰值下跌{drop:.1f}%)', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax4.text(bar.get_x() + bar.get_width()/2., height + 3,
                f'{height}万', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('gta_price_trend_chart.png', dpi=300, bbox_inches='tight')
print("图表3已保存: gta_price_trend_chart.png")

print("\n所有图表已生成完成！")
print("1. gta_price_sales_chart.png - 价格与销量对比")
print("2. gta_property_types_chart.png - 房产类型价格")
print("3. gta_price_trend_chart.png - 价格趋势图")