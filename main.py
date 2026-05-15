import requests
import pandas as pd
import time
import os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
print(f"📅 [오늘의 날짜] {today} - 와우 PvP 데이터 분석을 시작합니다.")

# 1. 저장할 폴더 4개 생성 (없으면 만들고, 있으면 넘어감)
folders = ["3v3_percentile", "shuffle_percentile", "3v3_tier_list", "shuffle_tier_list"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

wow_classes = {
    "death-knight": ["blood", "frost", "unholy"],
    "demon-hunter": ["havoc", "vengeance"],
    "druid": ["balance", "feral", "guardian", "restoration"],
    "evoker": ["augmentation", "devastation", "preservation"],
    "hunter": ["beast-mastery", "marksmanship", "survival"],
    "mage": ["arcane", "fire", "frost"],
    "monk": ["brewmaster", "mistweaver", "windwalker"],
    "paladin": ["holy", "protection", "retribution"],
    "priest": ["discipline", "holy", "shadow"],
    "rogue": ["assassination", "outlaw", "subtlety"],
    "shaman": ["elemental", "enhancement", "restoration"],
    "warlock": ["affliction", "demonology", "destruction"],
    "warrior": ["arms", "fury", "protection"]
}

ratings = list(range(1000, 2700, 100))
target_ratings = [2200, 2300, 2400, 2500] 
calc_ratings = [r - 100 for r in target_ratings]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 2. 파일 저장 경로에 폴더명 추가
brackets = {
    "3v3": {
        "url_part": "leaderboard-distrubution", 
        "raw_name": f"3v3_percentile/drustvar_3v3_raw_{today}.csv", 
        "tier_name": f"3v3_tier_list/wow_3v3_tier_ranking_{today}.csv"
    },
    "shuffle": {
        "url_part": "shuffle-distrubution", 
        "raw_name": f"shuffle_percentile/drustvar_shuffle_raw_{today}.csv", 
        "tier_name": f"shuffle_tier_list/wow_shuffle_tier_ranking_{today}.csv"
    }
}

for bracket_name, info in brackets.items():
    print(f"\n--- {bracket_name.upper()} 데이터 수집 시작 ---")
    current_df = pd.DataFrame(index=ratings)
    
    for cls, specs in wow_classes.items():
        for spec in specs:
            column_name = f"{cls.replace('-', ' ').title()} - {spec.replace('-', ' ').title()}"
            url = f"https://drustvar.com/api/v1/leaderboard/{info['url_part']}?search[region]=all&search[bracket]={bracket_name}&search[role]=spec&search[cc]={cls}&search[cs]={spec}"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json().get("stats", [])
                    for item in data:
                        rating = item["rating"]
                        if rating in current_df.index:
                            current_df.loc[rating, column_name] = item["percentile"]
            except Exception as e:
                print(f"[{column_name}] API 오류: {e}")
            time.sleep(0.5)

    current_df = current_df.ffill().fillna(0)
    current_df.index.name = "Rating"
    
    # 원본 파일 저장 (각각의 percentile 폴더로 들어감)
    current_df.to_csv(info["raw_name"], encoding="utf-8-sig")
    
    valid_targets = []
    valid_calcs = []
    for target, calc in zip(target_ratings, calc_ratings):
        if calc in current_df.index:
            valid_targets.append(target)
            valid_calcs.append(calc)
            
    if valid_calcs:
        df_top_pct = 100 - current_df.loc[valid_calcs]
        df_tier = df_top_pct.T
        df_tier.columns = [f"{int(r)}+ 상위 (%)" for r in valid_targets]
        sort_col = f"{int(valid_targets[0])}+ 상위 (%)"
        df_tier = df_tier.sort_values(by=sort_col, ascending=False).round(3)
        df_tier.index.name = "Class - Spec"
        
        # 티어 랭킹 파일 저장 (각각의 tier_list 폴더로 들어감)
        df_tier.to_csv(info["tier_name"], encoding="utf-8-sig")
        print(f"✅ {info['tier_name']} 저장 완료!")

print("\n🎉 오늘의 크롤링 및 분석이 모두 완료되었습니다!")
