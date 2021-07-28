"""
session = Site.get_session()
grid_type = Data.GridType.Radical
output_data = Data.get_grid_items(0.7, grid_type, session)
print(output_data)

output_data.to_csv(f"Japanese/Output/WaniKani_{ str(grid_type) }_Data.csv", index=False)
"""
