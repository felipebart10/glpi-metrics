from report_tools.dataframebuilder import DataFrameBuilder

data_frame = DataFrameBuilder('2021-10-01', '2021-10-31', 'actualtime', True)
data_frame.tickets_report_actualtime()
data_frame.export_excel(True)
#data_frame.quick_summary()