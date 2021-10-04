import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np

def stats(timeseries):
    format_string = "{0: >20,.0f}"
    print("       Average =" + format_string.format(np.mean(timeseries)))
    print(" 1% percentile =" + format_string.format(np.percentile(timeseries, 1)))
    print(" 5% percentile =" + format_string.format(np.percentile(timeseries, 5)))
    print("10% percentile =" + format_string.format(np.percentile(timeseries, 10)))
    print("25% percentile =" + format_string.format(np.percentile(timeseries, 25)))
    print("50% percentile =" + format_string.format(np.percentile(timeseries, 50)))
    print("75% percentile =" + format_string.format(np.percentile(timeseries, 75)))
    print("95% percentile =" + format_string.format(np.percentile(timeseries, 95)))
    print("99% percentile =" + format_string.format(np.percentile(timeseries, 99)))
    print("\n")

def find_first_negative(array):
    for idx, el in enumerate(array):
        if el < 0:
            return idx - 1
    return 1000

def age(dob, today = dt.date.today()):
    difference_in_years = relativedelta(today, dob).years
    difference_in_months = relativedelta(today, dob).months
    print(difference_in_months)
    if difference_in_months <= 6:
      years = difference_in_years
    else:
      years = difference_in_years + 1
    return years