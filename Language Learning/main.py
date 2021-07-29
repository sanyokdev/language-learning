import WaniKani

session = WaniKani.site.get_session()
grid_type = WaniKani.data.GridType.Kanji
output_data = WaniKani.data.get_grid_items(0.7, grid_type, session)
print(output_data)

output_data.to_csv(f"-Output/WaniKani_{ str(grid_type.name) }_Data.csv", index=False)
