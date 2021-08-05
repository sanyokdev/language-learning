import WaniKani
from WaniKani.data import CustomGridItem

session = WaniKani.site.get_session()

grid_type = WaniKani.data.GridType.Vocabulary
item_list = [
    CustomGridItem("Closet", "押入れ", "https://www.wanikani.com/vocabulary/%E6%8A%BC%E5%85%A5%E3%82%8C"),
    CustomGridItem("Feudalism", "封建主義", "https://www.wanikani.com/vocabulary/%E5%B0%81%E5%BB%BA%E4%B8%BB%E7%BE%A9"),
    CustomGridItem("Business", "営業", "https://www.wanikani.com/vocabulary/%E5%96%B6%E6%A5%AD"),
    CustomGridItem("To Put In", "込める", "https://www.wanikani.com/vocabulary/%E8%BE%BC%E3%82%81%E3%82%8B"),
    CustomGridItem("To Try", "試みる", "https://www.wanikani.com/vocabulary/%E8%A9%A6%E3%81%BF%E3%82%8B"),
    CustomGridItem("Six", "六", "https://www.wanikani.com/vocabulary/%E5%85%AD")
]

grid_data = WaniKani.data.get_custom_grid_data(item_list, grid_type)
# grid_data = WaniKani.data.get_grid_data(grid_type, session)

grid_item_data = WaniKani.data.get_grid_item_data(grid_data, session)
grid_item_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
print(grid_item_data)
