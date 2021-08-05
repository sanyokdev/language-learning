import WaniKani
from WaniKani.data import CustomGridItem

session = WaniKani.site.get_session()

grid_type = WaniKani.data.GridType.Vocabulary

item_list = [
    CustomGridItem("White Chrysanthemum", "白菊", "https://www.wanikani.com/vocabulary/%E7%99%BD%E8%8F%8A"),
    CustomGridItem("To Hang", "掛ける", "https://www.wanikani.com/vocabulary/%E6%8E%9B%E3%81%91%E3%82%8B"),
    CustomGridItem("Marriage", "結婚", "https://www.wanikani.com/vocabulary/%E7%B5%90%E5%A9%9A"),
    CustomGridItem("Frame", "枠組み", "https://www.wanikani.com/vocabulary/%E6%9E%A0%E7%B5%84%E3%81%BF")
]

grid_data = WaniKani.data.get_custom_grid_data(item_list, grid_type)
# grid_data = WaniKani.data.get_grid_data(grid_type, session)

grid_item_data = WaniKani.data.get_grid_item_data(grid_data, session, DEBUG=True, MAX_COUNT=20)
grid_item_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
print(grid_item_data)
