import numpy as np
import matplotlib.pyplot as plt
import sys
import json
import os
import datetime as dt
from taxes import net_to_gross
from utils import stats, age, find_first_negative


with open('inputs.json') as f:
    inputs = json.load(f)

# Personal data
starting_capital = inputs["personal"]['starting_capital']    # Starting capital
retirement_age = inputs["personal"]['retirement_age']        # Retirement age
# Number of samples for the Montecarlo simulation
samples = inputs["personal"]['samples']
dob = dt.datetime.strptime(inputs["personal"]['dob'], '%Y-%m-%d')
age = age(dob)
max_age = inputs["personal"]['max_age']             # The age you expect to die

# Allocation
current_stocks = inputs["allocation"]["current_stocks"]     # Starting stocks percentage in portfolio
current_bonds = (1 - current_stocks)                        # Starting bonds percentage in portfolio
# Because you are not getting any younger, each year the portfolio is rebalanced towards bonds by this percentage
stocks_to_bonds = inputs["allocation"]["stocks_to_bonds"]
min_stocks = inputs["allocation"]["min_stocks"]             # Minimum percentage of stocks in portfolio
max_bonds = (1.0 - min_stocks)                              # Calculated maximum percentage of bonds

# Returns and volatility
mu_stocks = inputs["returns"]["mu_stocks"]      # Stocks return after inflation
mu_bonds = inputs["returns"]["mu_bonds"]        # Bonds return after inflation
vol_stocks = inputs["returns"]["vol_stocks"]    # Stocks volatility (standard deviation)
vol_bonds = inputs["returns"]["vol_bonds"]      # Bonds volatility (standard deviation)


# Contribution before retirement
# Monthly personal contribution without government topup (Net). This does not include work match
personal_contribution = inputs["contributions"]["personal"]
# Monthly work contribution without government topup. Multiply by 2 if you match the company contribution
employee_contribution = inputs["contributions"]["employee"]
employer_contribution = inputs["contributions"]["employer"]
work_contribution = employee_contribution + employer_contribution
annual_contribution = 12.0 * personal_contribution + 12 * work_contribution
contribution_growth = inputs["contributions"]["growth"]  # Because of payrise for example
gov_topup = inputs["contributions"]["gov_topup"]         # Higher tax rate. This is valid only in UK and as of 2021
# If for example you have other sources of income
contribution_during_retirement = inputs["contributions"]["retirement"]


# Expenses during retirement. During working years expenses do not count
annual_expenses = 12 * inputs["retirement"]["monthly_expenses"]          # Net expenses once you retire.
tax_free_allowance = inputs["retirement"]["tax_free_allowance"]          # Valid in UK
state_pension = inputs["retirement"]["state_pension"]                    # After 66 as of 2021
state_pension_age = inputs["retirement"]["state_pension_age"]            # As of 2021


# Taxes calculation
# Because I need to pay taxes on withdrwal it means that I have to withdraw
# more to cover expenses
sustainable_withdrawal_rate = False     # Need to review
swr_percentage = 0.04                   # Need to review
bands = inputs["tax"]['tax_bands']
rates = inputs["tax"]['tax_rates']




# You pay taxes only on 75% of what you take out of your pension.
# This assumes that you do not take a lump sum
taxable_annual_expenses = (1 - tax_free_allowance) * annual_expenses
annual_withdrawal = net_to_gross(taxable_annual_expenses, bands, rates) + \
    tax_free_allowance * annual_expenses  # Total gross withdrawal


living_years = max_age - age                    # Number of years left
# Number of working years based on your expected retiremen age
working_years = retirement_age - age
state_pension_years = state_pension_age - \
    age   # Number of years before state pension
print("\nAge:                     " + str(age))
print("Retirement age:          " + str(retirement_age))
print("Annual withdrawal        " + str(annual_withdrawal))
print("Working years:           " + str(working_years))
print("No state pension years:  " + str(working_years))
print("Years left:              " + str(living_years))


final_value = []
value_55 = []
value_retirement = []
value_85 = []
value_100 = []
zero_capital_year = []
min_annual_withdrawals = []

print('Samples: ' + str(samples))
for i in range(samples):
    if i % (samples / 10) == 0:
        iteration_text = str(i) + '.. '
        sys.stdout.write(iteration_text)

    annual_investment = annual_contribution * (1.0 + gov_topup)
    stocks = current_stocks
    bonds = current_bonds

    # Create list of daily returns using random normal distribution
    annual_returns_stocks = np.random.normal(
        mu_stocks, vol_stocks, living_years)
    annual_returns_bonds = np.random.normal(mu_bonds, vol_bonds, living_years)

    # Set starting capital and create annual capital series generated by above random daily returns
    annual_values = [starting_capital]
    annual_withdrawals = []

    # Year is a counter from now
    for year, (annual_return_stocks, annual_return_bonds) in enumerate(zip(annual_returns_stocks, annual_returns_bonds)):

        # Assume we invest at the end of the year - Conservative assumption I think
        if year <= working_years:  # Before retirement
            starting_annual_value = annual_values[-1]  # From previous year
            final_annual_value = stocks * starting_annual_value * (annual_return_stocks + 1.0) + \
                bonds * starting_annual_value * \
                (annual_return_bonds + 1.0)     # Change of previous year capital
            # Additional investemnt at the end of year
            annual_values.append(final_annual_value + annual_investment)
        else:  # After retirement
            # Assume we withdraw at the beginning of the year - Conservative assumption
            if sustainable_withdrawal_rate:  # To be reviewed. Ignore for now
                if swr_percentage * annual_values[-1] > annual_withdrawal:
                    actual_annual_withdrawal = annual_withdrawal
                else:
                    actual_annual_withdrawal = swr_percentage * \
                        annual_values[-1]
            else:
                if year <= state_pension_years:
                    # I need to withdraw all expected expenses
                    actual_annual_withdrawal = annual_withdrawal
                else:
                    actual_annual_withdrawal = annual_withdrawal - \
                        state_pension  # Little help from state pension
            annual_withdrawals.append(actual_annual_withdrawal)

            starting_annual_value = annual_values[-1] - \
                actual_annual_withdrawal
            final_annual_value = stocks * starting_annual_value * (annual_return_stocks + 1.0) + \
                bonds * starting_annual_value * (annual_return_bonds + 1.0)
            annual_values.append(final_annual_value)

        if year <= working_years:                               # Before retirement
            # Keep investing until retiremnt
            annual_investment *= (1.0 + contribution_growth)
        else:                                                   # After retirement - No growth
            # Assume it will not increase. Safely I assume 0.0
            annual_investment = contribution_during_retirement

        # Limit stocks contribution to min_stocks%
        stocks = max(min_stocks, stocks - stocks_to_bonds)
        # Limit bonds contribution to max_bonds%
        bonds = min(max_bonds, bonds + stocks_to_bonds)

    # This is only valid if sustainable_withdrawal_rate == True
    min_annual_withdrawal = min(annual_withdrawals)

    # Generate Plots - price series and histogram of daily returns
    # plt.plot(annual_values)

    # Let's create some statistics at various ages
    year_55 = 55 - age  # Minimum retirement age in UK as of 2020
    value_55.append(annual_values[year_55])

    year_retirement = retirement_age - age
    value_retirement.append(annual_values[year_retirement])

    year_85 = 85 - age
    value_85.append(annual_values[year_85])

    year_100 = 100 - age
    value_100.append(annual_values[year_100])

    final_value.append(annual_values[-1])

    zero_capital_year.append(find_first_negative(annual_values) + age)

    min_annual_withdrawals.append(min_annual_withdrawal)

print("\nFinal stocks/bonds: " + str(stocks) + "/" + str(bonds))

print("\nMin withdrawal (TODO: SWR - IGNORE FOR NOW")
stats(min_annual_withdrawals)

print("\nValue at the 55")
stats(value_55)

print("\nValue at the retirement (" + str(retirement_age) + ")")
stats(value_retirement)

print("\nValue at the 85")
stats(value_85)

print("\nValue at the 100")
stats(value_100)

print("\nValue at the end (" + str(max_age) + ")")
stats(final_value)

print("\nZero capital age")
stats(zero_capital_year)
