import WaniKani
from WaniKani.data import CustomGridItem

session = WaniKani.site.get_session()
grid_type = WaniKani.data.GridType.Vocabulary


item_list = [
    CustomGridItem("Precision", "精度", "https://www.wanikani.com/vocabulary/%E7%B2%BE%E5%BA%A6"),
    CustomGridItem("Existing", "既存", "https://www.wanikani.com/vocabulary/%E6%97%A2%E5%AD%98"),
    CustomGridItem("Only", "唯一", "https://www.wanikani.com/vocabulary/%E5%94%AF%E4%B8%80"),
    CustomGridItem("Cave", "洞穴", "https://www.wanikani.com/vocabulary/%E6%B4%9E%E7%A9%B4"),
    CustomGridItem("Secretion", "分泌", "https://www.wanikani.com/vocabulary/%E5%88%86%E6%B3%8C"),
    CustomGridItem("Diarrhea", "下痢", "https://www.wanikani.com/vocabulary/%E4%B8%8B%E7%97%A2")
]
grid_data = WaniKani.data.get_custom_grid_data(item_list, grid_type)

# grid_data = WaniKani.data.get_grid_data(grid_type, session)
grid_item_data = WaniKani.data.get_grid_item_data(grid_data, session)

grid_item_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
print(grid_item_data)
