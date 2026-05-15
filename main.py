import requests
import pandas as pd
import time
import os
from datetime import datetime
import matplotlib.pyplot as plt

plt.switch_backend('Agg')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# --- [설정 및 색상 정의] ---
CHART_DAYS = 60
VIEW_RANK_LIMIT = 10

# 와우 직업별 공식 색상 (Hex Code)
CLASS_COLORS = {
    "Death Knight": "#C41E3A", "Demon Hunter": "#A330C9", "Druid": "#FF7C0A",
    "Evoker": "#33937F", "Hunter": "#AAD372", "Mage": "#3FC7EB",
    "Monk": "#00FF98", "Paladin": "#F48CBA", "Priest": "#FFFFFF",
    "Rogue": "#FFF468", "Shaman": "#0070DD", "Warlock": "#8788EE",
    "Warrior": "#C69B6D"
}

# ------------------

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [시각화 개선] {today} - 가독성을 높인 그래프 생성을 시작합니다.")

# (기존 폴더 생성 및 wow_classes 정의 생략 - 이전과 동일하게 유지)
# ... [중략: 폴더 생성 및 데이터 수집 로직은 그대로 사용하세요] ...

# 3. 점수대별 시각화 로직 (이 부분이 핵심 수정 사항입니다)
for mode in ["3v3", "shuffle"]:
    # ... [중략: 데이터 수집 및 csv 저장 로직] ...
    
    for target in target_ratings:
        # ... [중략: 히스토리 데이터 로드 로직] ...
        
        plt.figure(figsize=(16, 9), facecolor='#1e1e1e') # 어두운 배경 테마
        ax = plt.gca()
        ax.set_facecolor('#1e1e1e')
        
        latest_ranks = df_hist.iloc[-1].sort_values()
        sorted_specs = latest_ranks.index

        for spec in sorted_specs:
            plot_data = df_hist[spec].tail(CHART_DAYS)
            is_top_10 = latest_ranks[spec] <= VIEW_RANK_LIMIT
            
            # 직업 이름 추출하여 색상 매칭 (예: "Mage - Frost" -> "Mage")
            class_name = spec.split(" - ")[0]
            line_color = CLASS_COLORS.get(class_name, "#888888")
            
            if is_top_10:
                # Top 10은 굵고 진하게, 범례(label) 등록
                plt.plot(plot_data.index, plot_data.values, marker='o', 
                         markersize=6, linewidth=3.5, color=line_color, 
                         alpha=1.0, label=f"[{int(latest_ranks[spec])}위] {spec}")
            else:
                # 10위 밖은 얇고 투명하게, 범례에서 제외 (label 생략)
                plt.plot(plot_data.index, plot_data.values, color=line_color, 
                         linewidth=0.8, alpha=0.15)

        plt.title(f"{target}+ {mode.upper()} Top 10 Trend", fontsize=20, pad=30, color='white')
        plt.ylabel("Rank", fontsize=14, color='white')
        
        plt.gca().invert_yaxis()
        plt.ylim(VIEW_RANK_LIMIT + 0.5, 0.5)
        plt.yticks(range(1, VIEW_RANK_LIMIT + 1), color='white')
        plt.xticks(rotation=45, color='white')
        
        # 그리드 및 테두리 색상 조정
        plt.grid(True, axis='y', linestyle='--', alpha=0.2, color='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#444444')
            
        # 범례 설정: Top 10만 깔끔하게 우측 배치
        if not df_hist.empty:
            plt.legend(title="Top 10 Specs Today", bbox_to_anchor=(1.02, 1), 
                       loc='upper left', fontsize=11, facecolor='#2d2d2d', 
                       edgecolor='#444444', labelcolor='white')
        
        plt.tight_layout()
        plt.savefig(f"plots/{mode}_{target}_trend.png", dpi=150, facecolor='#1e1e1e')
        plt.close()
