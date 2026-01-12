from django.core.validators import URLValidator

from openpyxl import load_workbook, workbook


wb = load_workbook("upload_example.xlsx")

ws = wb.active

# for row in ws.iter_rows(min_row=1, max_col=5, values_only=True):
#     print(row)

result_dict = {}

for column in ws.iter_cols(values_only=True):
    header = column[0]
    values = [val for val in column[1:] if val is not None]
        
    result_dict[header] = values
print(result_dict)
