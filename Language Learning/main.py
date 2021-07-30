import WaniKani

session = WaniKani.site.get_session()
grid_type = WaniKani.data.GridType.Vocabulary

grid_data = WaniKani.data.get_grid_data(grid_type, session)
grid_item_data = WaniKani.data.get_grid_item_data(grid_data, session)

grid_item_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
print(grid_item_data)
