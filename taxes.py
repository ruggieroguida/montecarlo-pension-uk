import numpy as np

bands = [12500.0, 14549.0, 24944.0, 43430.0, 150000.0, 1000000.0]
rates = [    0.0,    19.0,    20.0,    21.0,     41.0,      46.0]

def gross_to_net(gross_income, bands, rates):
  gross_income = float(gross_income)

  chunks = []
  for i in range(len(bands)):
    if i == 0:
      chunk = bands[i]
    else:
      chunk = bands[i] - bands[i-1]
    chunks.append(chunk)

  my_chunks = []
  current_taxable_gross = 0
  for chunk in chunks:
    current_taxable_gross += chunk
    if current_taxable_gross <= gross_income:
      my_chunks.append(chunk)
      previous_taxable_gross = current_taxable_gross
    else:
      my_current_chunk = max(gross_income - previous_taxable_gross, 0.0)
      my_chunks.append(my_current_chunk)
      previous_taxable_gross = current_taxable_gross

  income_taxes = np.dot(my_chunks, np.divide(rates, 100.0))

  # def gross_to_net(gross_income):
  print(chunks)
  print(my_chunks)
  print(sum(my_chunks))

  print(income_taxes)
  income = gross_income - income_taxes
  print(income)

  weekly_earnings = gross_income / 52.0
  print(weekly_earnings)

  national_insurance_weekly = 0
  if weekly_earnings <= 166.0:
    national_insurance_weekly = 0.0
  elif weekly_earnings <= 962.0:
    national_insurance_weekly = (weekly_earnings - 166.0) * 0.12
  elif weekly_earnings > 962.0:
    national_insurance_weekly = (962.0 - 166.0) * 0.12 + (weekly_earnings - 962.0) * 0.02

  print(national_insurance_weekly)
  national_insurance = 52.0 * national_insurance_weekly
  print(national_insurance)

  net_income = income - national_insurance
  print(net_income)


# This exclude national insurance because it is not paid after retirement
def net_to_gross(net_income, bands, rates):
  net_income = float(net_income)
  chunks = []
  for i in range(len(bands)):
    if i == 0:
      chunk = bands[i]
    else:
      chunk = bands[i] - bands[i-1]
    chunks.append(chunk)
  # print(chunks)

  net_chunks = []
  for i, chunk in enumerate(chunks):
    net_chunk = chunk * (1.0 - rates[i] / 100.0)
    net_chunks.append(net_chunk)
  
  # print(net_chunks)

  gross_income = 0
  current_net = 0
  previous_net = 0
  for net_chunk, chunk in zip(net_chunks, chunks):
    current_net += net_chunk
    if net_income >= current_net:
      # ratio = (net_income - previous_net) / net_chunk
      gross_income += chunk
      previous_net = current_net
    else:
      ratio = (net_income - previous_net) / net_chunk
      gross_income += chunk * ratio
      break

  # print(gross_income)
  return gross_income


# gross_to_net(625000, bands, rates)
# print()
gross_income = net_to_gross(30000, bands, rates)
print(gross_income)