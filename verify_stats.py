#!/usr/bin/env python3
"""verify_stats.py — 论文统计声明的精确复核（零依赖）。

verify_core.py 检查数据层（映射表、循环分解、汉明分布）；
本脚本检查论文中的统计推断层：每个随机基线和显著性数字的封闭公式值。

所有公式均为 S_n 随机置换的标准结果：
- 特定循环型 (c1,...,ck)（各长度互异）的概率 = 1/(c1*...*ck)
- 循环数的期望 = H_n，方差 = H_n - H_n^(2)
- 最大循环长度 L > n/2 时 P(max = L) = 1/L
- 固定点数 → Poisson(1)，P(0) → 1/e
- 相邻对汉明距离基线：随机置换中相邻两卦必不同，
  P(d=k) = C(6,k)/63（k≥1），63 个相邻对
"""
from math import comb, e
from fractions import Fraction

n = 64
PASS = True

def check(label, actual, expect, tol=0.0005):
    global PASS
    ok = abs(actual - expect) <= tol * max(1, abs(expect))
    print(f"{'ok ' if ok else 'FAIL'} {label}: {actual:.6g} (期望 {expect})")
    if not ok:
        PASS = False

# 1. 循环型 (52,10,2) 的精确概率 = 1/(52*10*2) = 1/1040
p_type = Fraction(1, 52 * 10 * 2)
print(f"-- 循环型 (52,10,2) 精确概率 = 1/{p_type.denominator} = {float(p_type)*100:.4f}%")
check("P(cycle type) %", float(p_type) * 100, 0.09615, 0.001)

# 2. 循环数：期望 H_64、标准差 sqrt(H_64 - H_64^(2))、z 值
H1 = sum(Fraction(1, k) for k in range(1, n + 1))
H2 = sum(Fraction(1, k * k) for k in range(1, n + 1))
mean_c, var_c = float(H1), float(H1 - H2)
sd_c = var_c ** 0.5
z = (3 - mean_c) / sd_c
print(f"-- 循环数: 期望 {mean_c:.4f}, 标准差 {sd_c:.4f}, 实际 3 → z = {z:.2f}")
check("循环数期望 H_64", mean_c, 4.7439, 0.001)
check("循环数标准差", sd_c, 1.7661, 0.001)
check("z 值", z, -0.99, 0.02)

# 3. 最大循环: 期望 ≈ Golomb–Dickman * n；P(max >= 52) = H_64 - H_51（L>n/2 区间）
p_max_ge_52 = float(sum(Fraction(1, L) for L in range(52, n + 1)))
print(f"-- P(最大循环 >= 52) = {p_max_ge_52:.4f}（不是极端事件）")
check("P(max cycle >= 52)", p_max_ge_52, 0.2270, 0.005)
check("最大循环期望 ~ 0.6243*64", 0.62432998854 * n, 39.96, 0.001)

# 4. 固定点: P(0) = D_64/64! ≈ 1/e
check("P(固定点=0) ≈ 1/e", 1 / e, 0.3679, 0.001)

# 5. 相邻对汉明基线（随机置换，63 对，条件于两卦不同）
pairs = 63
exp_d6 = pairs * comb(6, 6) / 63
exp_dle2 = pairs * (comb(6, 1) + comb(6, 2)) / 63
exp_dge4 = pairs * (comb(6, 4) + comb(6, 5) + comb(6, 6)) / 63
mean_d = sum(k * comb(6, k) for k in range(1, 7)) / 63
print(f"-- 随机置换基线: E[d=6对]={exp_d6:.2f}, E[d<=2对]={exp_dle2:.2f}, "
      f"E[d>=4对]={exp_dge4:.2f}, E[平均d]={mean_d:.4f}")
check("E[d=6 对数]", exp_d6, 1.0)
check("E[d<=2 对数]", exp_dle2, 21.0)
check("E[d>=4 对数]", exp_dge4, 22.0)
check("E[相邻平均汉明]（置换基线）", mean_d, 3.0476, 0.001)
# 独立均匀对（非置换）基线是 3.000——论文旧表用的是这个，两者需区分
check("E[相邻平均汉明]（独立对基线）", 6 * 0.5, 3.0)

# 6. 偶:奇 汉明步基线（随机置换）
p_even = (comb(6, 2) + comb(6, 4) + comb(6, 6)) / 63
print(f"-- 随机置换偶数步比例 = {p_even:.4f} → 偶:奇 ≈ {p_even/(1-p_even):.2f}:1")
check("随机偶:奇比", p_even / (1 - p_even), 0.969, 0.005)

print("\n" + ("ALL OK" if PASS else "存在 FAIL — 论文数字与公式不符"))
raise SystemExit(0 if PASS else 1)
