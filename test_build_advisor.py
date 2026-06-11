from src.core.build_advisor import BuildAdvisor

advisor = BuildAdvisor()

for item in advisor.recommend_for_weapon(
    "Phenmor"
):
    print(item)