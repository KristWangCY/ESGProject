import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pmdarima as pm
import warnings

warnings.filterwarnings("ignore")

US_emissions = pd.read_excel('US_emissions.xlsx')

US_emissions_1 = US_emissions.drop(US_emissions.columns[[2, 3, 4, 5, 6, 8, 16]], axis=1)
US_emissions_2 = US_emissions_1.groupby(['year', 'parent_entity'], as_index=False).sum(numeric_only=True)
US_emissions_recent = US_emissions_2[US_emissions_2['year'] >= 2000]

emissions_by_year = US_emissions_recent.groupby('year')['total_operational_emissions_MtCO2e'].sum().reset_index()

emissions_ts = emissions_by_year.set_index('year')['total_operational_emissions_MtCO2e']

auto_model = pm.auto_arima(emissions_ts, seasonal=False, stepwise=True, trace=False)
print(auto_model.summary())

# Forecasting the next 25 years
forecast_years = 25
forecast, conf_int = auto_model.predict(n_periods=forecast_years, return_conf_int=True)

forecast_years_index = np.arange(emissions_ts.index[-1] + 1, emissions_ts.index[-1] + forecast_years + 1)

# Plotting the forecast
plt.figure(figsize=(12, 7))
plt.plot(emissions_ts.index, emissions_ts.values, marker='o', label='Historical Emissions')
plt.plot(forecast_years_index, forecast, marker='o', linestyle='--', color='red', label='Forecasted Emissions')
plt.fill_between(forecast_years_index, conf_int[:, 0], conf_int[:, 1], color='pink', alpha=0.3, label='Confidence Interval')

final_forecast_value = forecast.iloc[-1]
plt.axhline(y=final_forecast_value, color='green', linestyle=':', linewidth=2, label=f'Final Forecasted Level: {final_forecast_value:.2f} MtCO2e')
plt.text(forecast_years_index[-1], final_forecast_value, f'{final_forecast_value:.2f}', color='green', fontsize=15, verticalalignment='bottom')

plt.title('ARIMA Forecast of Operational Emissions with Approaching Level')
plt.xlabel('Year')
plt.ylabel('Total Operational Emissions (MtCO2e)')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
