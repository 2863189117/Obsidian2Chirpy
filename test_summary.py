#!/usr/bin/env python
"""
测试AI摘要生成功能
"""

import os
import sys
from obsidian2chirpy.utils import ai_utils
from obsidian2chirpy.config import settings

def test_summary():
    """测试AI摘要生成功能"""
    
    # 检查是否提供了API密钥
    if not settings.AI_API_KEY:
        api_key = input("请输入AI API密钥（按Enter取消）: ").strip()
        if not api_key:
            print("未提供API密钥，测试取消")
            return
        settings.AI_API_KEY = api_key
    
    # 测试文本
    test_text = """
# 引力辐射理论

此处的推导 follow Weinberg 的《引力与宇宙学》，平行的推导见*引力辐射(Maggiore)*。
Einstein 场方程和 Maxwell 方程都具有辐射解。因为场方程本身是非线性的，于是我们先仅仅研究弱场辐射。也就是引力波本身的$T_{\mu \nu}$弱到不影响自己。

## 弱场近似
我们假设度规接近 Minkowski 度规$\eta_{\mu \nu}$：

$$g_{\mu\nu}=\eta_{\mu\nu}+h_{\mu\nu}$$

其中$\vert h_{\mu \nu}\vert \ll_{1}$，近似到$h$的一阶，Ricci 张量变为：

$$R_{\mu\nu}\simeq\frac{\partial}{\partial x^\nu}\Gamma_{\lambda\mu}^\lambda-\frac{\partial}{\partial x^\lambda}\Gamma_{\mu\nu}^\lambda+\bigcirc(h^2)$$

仿射联络：

$$\Gamma_{\mu\nu}^{\lambda}=\frac{1}{2}\eta^{\lambda\rho}\left[\frac{\partial}{\partial x^{\mu}}h_{\rho\nu}+\frac{\partial}{\partial x^{\nu}}h_{\rho\mu}-\frac{\partial}{\partial x^{\rho}}h_{\mu\nu}\right]+\bigcirc(h^{2})$$
"""

    print("正在使用AI生成文章摘要...")
    summary = ai_utils.generate_summary(test_text)
    
    if summary:
        print("\n✅ 摘要生成成功:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        print(f"摘要长度: {len(summary)} 个字符")
    else:
        print("\n❌ 摘要生成失败")

if __name__ == "__main__":
    test_summary()
