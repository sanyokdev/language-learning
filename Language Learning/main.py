import WaniKani
from WaniKani.data import CustomGridItem

grid_type = WaniKani.data.GridType.Radical

# item_list = [
#     CustomGridItem("", "", "")
# ]

# grid_data = WaniKani.data.get_custom_grid_data(item_list, grid_type)
grid_data = WaniKani.data.get_grid_data(grid_type)
grid_item_data = WaniKani.data.get_grid_item_data(grid_data, CHUNK_MODE=False, MAX_CHUNK_SIZE=1000)
