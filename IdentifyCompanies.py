import pandas as pd

# Load the dataset
emissions_df = pd.read_excel('US_emissions.xlsx')

# Compute Scope 1 and Scope 3
emissions_df['Scope_1'] = emissions_df['total_operational_emissions_MtCO2e']
emissions_df['Scope_3'] = emissions_df['total_emissions_MtCO2e'] - emissions_df['total_operational_emissions_MtCO2e']

# Select the most recent two years for comparison
recent_years = sorted(emissions_df['year'].unique())[-2:]
recent_emissions = emissions_df[emissions_df['year'].isin(recent_years)]

# Aggregate data to remove duplicate entries
aggregated_emissions = recent_emissions.groupby(['year', 'parent_entity'], as_index=False).agg({
    'Scope_1': 'sum',
    'Scope_3': 'sum',
    'production_value': 'sum'
})
print(aggregated_emissions)

# Pivot table to compare the emissions by company
pivot_emissions = aggregated_emissions.pivot(index='parent_entity', columns='year', values=['Scope_1', 'Scope_3', 'production_value'])



# Methodology 4: Detecting Greenwashing Patterns
# Condition 1: Scope 1 stable or rising, Scope 3 sharply drops, 0.8 threshold. - Result is empty
condition1 = pivot_emissions[
    (pivot_emissions['Scope_1'][recent_years[-1]] >= pivot_emissions['Scope_1'][recent_years[-2]]) &
    (pivot_emissions['Scope_3'][recent_years[-1]] < pivot_emissions['Scope_3'][recent_years[-2]] * 0.8)
]

# Condition 2: Scope 1 and Scope 3 decrease together
condition2 = pivot_emissions[
    (pivot_emissions['Scope_1'][recent_years[-1]] < pivot_emissions['Scope_1'][recent_years[-2]]) &
    (pivot_emissions['Scope_3'][recent_years[-1]] < pivot_emissions['Scope_3'][recent_years[-2]])
]

# Condition 3: Production increases, Scope 1 does not decrease proportionally
condition3 = pivot_emissions[
    (pivot_emissions['production_value'][recent_years[-1]] > pivot_emissions['production_value'][recent_years[-2]]) &
    (pivot_emissions['Scope_1'][recent_years[-1]] >= pivot_emissions['Scope_1'][recent_years[-2]] * 0.95)
]

final_df = pd.concat({
    'Reliance on offsets (Condition 1)': condition1,
    'Credible reductions (Condition 2)': condition2,
    'Efficiency claims verification (Condition 3)': condition3
}, axis=0)
# Print the results directly
print(final_df)
print(condition1)
# Save the results to a new Excel file
# final_df.to_excel('company_conditions.xlsx')




# Methodology 5: Cluster Companies Based on Greenwashing Risk
# True Reducers: Scope 1 and Scope 3 both decrease
true_reducers = pivot_emissions[
    (pivot_emissions['Scope_1'][recent_years[-1]] < pivot_emissions['Scope_1'][recent_years[-2]]) &
    (pivot_emissions['Scope_3'][recent_years[-1]] < pivot_emissions['Scope_3'][recent_years[-2]])
]

# Offset-Heavy Companies: High Scope 3 reduction (>10%), Scope 1 stable or increasing - Result is empty
offset_heavy = pivot_emissions[
    (pivot_emissions['Scope_1'][recent_years[-1]] >= pivot_emissions['Scope_1'][recent_years[-2]]) &
    (pivot_emissions['Scope_3'][recent_years[-1]] < pivot_emissions['Scope_3'][recent_years[-2]] * 0.9)
]

# Potential Greenwashers: Scope 1 change insignificant (within ±10%), high Scope 3 reduction - Result is empty
potential_greenwashers = pivot_emissions[
    (pivot_emissions['Scope_1'][recent_years[-1]] >= pivot_emissions['Scope_1'][recent_years[-2]] * 0.9) &
    (pivot_emissions['Scope_1'][recent_years[-1]] <= pivot_emissions['Scope_1'][recent_years[-2]] * 1.1) &
    (pivot_emissions['Scope_3'][recent_years[-1]] < pivot_emissions['Scope_3'][recent_years[-2]] * 0.9)
]

# Combining results
clustered_df = pd.concat({
    'True Reducers': true_reducers,
    'Offset-Heavy Companies': offset_heavy,
    'Potential Greenwashers': potential_greenwashers
}, axis=0)

# Print final results
print("Clustered Companies Based on Greenwashing Risk:")
print(clustered_df)

# Optionally export results to Excel
clustered_df.to_excel("Clustered_Companies_Greenwashing_Risk.xlsx")