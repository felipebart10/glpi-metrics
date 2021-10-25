import calendar

pairs =[]

for year in range(2019,2022):
    for month in range(1, 13):
        pair = [f'{year}-{month:02d}-01', f'{year}-{month:02d}-{calendar.monthrange(year, month)[1]}']
        pairs.append(pair)


print(pairs)