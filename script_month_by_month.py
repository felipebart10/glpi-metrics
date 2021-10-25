from report_tools.gradescalculator3 import grade_calculator, compute_time_grades, get_monthly_quantity_bonus, average_grade, grade_summary
from report_tools.query_builder import export_excel
import pandas as pd

date_pairs = [['2021-01-01', '2021-01-31'], ['2021-02-01', '2021-02-28'], ['2021-03-01', '2021-03-31'], ['2021-04-01', '2021-04-30'], ['2021-05-01', '2021-05-31'], ['2021-06-01', '2021-06-30'], ['2021-07-01', '2021-07-31'], ['2021-08-01', '2021-08-31'], ['2021-09-01', '2021-09-30']]

df_list = []
for pair in date_pairs:
    df = grade_calculator(pair[0], pair[1])
    compute_time_grades(df, 'fechamento')
    compute_time_grades(df, 'solucao')
    average_grade(df, 1, 3)
    get_monthly_quantity_bonus(df, bonus_percentual=0.5)
    df_list.append(df)

df = pd.concat(df_list)
df_pivot = grade_summary(df)

export_excel(df, 'grades', start_file=True)
export_excel(df_pivot, 'summary', start_file=True)

