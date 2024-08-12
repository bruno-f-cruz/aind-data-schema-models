import pandas as pd

# Load the two CSV files into DataFrames
mouse_ccf_structures = pd.read_csv('mouse_ccf_structures.csv')
ontology_structure_minimal = pd.read_csv('ontology_structure_minimal.csv')

# Merge the two DataFrames based on the 'id' column
merged_df = mouse_ccf_structures.merge(
    ontology_structure_minimal[['id', 'color_hex_code']],
    on='id',
    how='left'
)

# Save the result back to a CSV file
merged_df.to_csv('mouse_ccf_structures_with_colors.csv', index=False)