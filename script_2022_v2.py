from report_tools.dataframebuilder import DataFrameBuilder

data_frame = DataFrameBuilder('2021-10-01', '2021-10-31', 'grades', True)
data_frame.quick_report()
data_frame = DataFrameBuilder('2021-10-01', '2021-10-31', 'summary', True)
#data_frame.quick_summary()