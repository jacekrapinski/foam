import pandas as pd
from glob import glob 
from xlsxwriter.utility import xl_col_to_name
import csv
import pandas as pd

def try_float(cell):
    try:
        return float(cell)
    except (ValueError, TypeError):
        return cell

def move_time_to_last(row):
    values = [val for val in row if val != 'NA']
    index = len(values)-1
    rlist=list(row)
    rlist[-1]=row[index]
    rlist[index]='NA'     
    return pd.Series(rlist)

def koloruj_wartosci(val):
    return 'color: green' if val < 0.9 else ''

# Read raw CSV rows into a list
with open("./wyniki/combined.csv", newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)

# Find the maximum number of columns in any row
max_len = max(len(row) for row in rows)

# Pad each row to the maximum length with 'NA'
padded_rows = [row + ['NA'] * (max_len - len(row)) for row in rows]

# Load into pandas
df = pd.DataFrame(padded_rows)

df=df.apply(move_time_to_last,axis=1)
df = df.applymap(try_float)

for col in df.columns:    
    df[col] = pd.to_numeric(df[col], errors='ignore')

print(df)

# df.to_excel('combined.xlsx',engine='openpyxl',index=False)


with pd.ExcelWriter("szybki.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Dane", index=False)
    workbook  = writer.book
    worksheet = writer.sheets["Dane"]
    
    # Format dla wartości < 50
    format_red = workbook.add_format({'bg_color': "#FF001E", 'font_color': "#000000"})
    format_orange = workbook.add_format({'bg_color': "#EE7118", 'font_color': '#000000'})
    format_yellow = workbook.add_format({'bg_color': "#F6FA03", 'font_color': '#000000'})
    format_green = workbook.add_format({'bg_color': "#0EF635", 'font_color': '#000000'})
    format_white = workbook.add_format({'bg_color': "#FFFFFF", 'font_color': '#000000'})

    # Dodaj formatowanie warunkowe do kolumny B (indeksowana od 0)

    mini=0.95-0.0135
    maxi=0.95+0.0135
    for col in range(10,51,4):        
        worksheet.conditional_format(f"{xl_col_to_name(col)}2:{xl_col_to_name(col)}3000", {
            'type':     'cell',
            'criteria': 'between',
            'minimum': mini,
            'maximum': maxi,
            'format':   format_green
        })

    mini=0.95-2*0.0135
    maxi=0.95+2*0.0135
    for col in range(10,51,4):
        worksheet.conditional_format(f"{xl_col_to_name(col)}2:{xl_col_to_name(col)}3000", {
            'type':     'cell',
            'criteria': 'between',
            'minimum': mini,
            'maximum': maxi,
            'format':   format_yellow
        })

    mini=0.95-3*0.0135
    maxi=0.95+3*0.0135
    for col in range(10,51,4):
        worksheet.conditional_format(f"{xl_col_to_name(col)}2:{xl_col_to_name(col)}3000", {
            'type':     'cell',
            'criteria': 'between',
            'minimum': mini,
            'maximum': maxi,
            'format':   format_orange
        })

    mini=0.95-4*0.0135
    maxi=0.95+4*0.0135
    for col in range(10,51,4):
        worksheet.conditional_format(f"{xl_col_to_name(col)}2:{xl_col_to_name(col)}3000", {
            'type':     'cell',
            'criteria': 'between',
            'minimum': mini,
            'maximum': maxi,
            'format':   format_red
        })
    
    

    

    

    for col in range(10,51,4):
        worksheet.conditional_format(f"{xl_col_to_name(col)}2:{xl_col_to_name(col)}3000", {
            'type':     'cell',
            'criteria': '=',
            'value': 'NA',            
            'format':   format_white
        })
