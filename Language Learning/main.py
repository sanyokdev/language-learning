import WaniKani
from WaniKani.data import CustomGridItem

session = WaniKani.site.get_session()

grid_type = WaniKani.data.GridType.Radical
"""
item_list = [
    CustomGridItem("", "", "")
]

grid_data = WaniKani.data.get_custom_grid_data(item_list, grid_type)
"""
grid_data = WaniKani.data.get_grid_data(grid_type, session)

grid_item_data = WaniKani.data.get_grid_item_data(grid_data, session)
grid_item_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
print(grid_item_data)
