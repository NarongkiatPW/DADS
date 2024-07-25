import gspread
from gspread_dataframe import set_with_dataframe
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output, ctx, callback, State, callback_context
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
from collections import OrderedDict
import plotly.express as px
import dash_bootstrap_components as dbc

### Import Data ###
# Bank_Coding Sheet
sheet_url = 'xxx' #### เนื่องจากเป็นความลับของบริษัทจึงไม่สามารถเผยแพร่ได้
csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
df_coding = pd.read_csv(csv_export_url)

# GL Sheet
sheet_url = 'xxx' #### เนื่องจากเป็นความลับของบริษัทจึงไม่สามารถเผยแพร่ได้
csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
df_GL  = pd.read_csv(csv_export_url)
# print(df_GL.head())

### Clean Data ###
df_coding['ถอนเงิน'] = df_coding['ถอนเงิน'].str.replace(',', '').astype(float).fillna(0)
df_coding['ฝากเงิน'] = df_coding['ฝากเงิน'].fillna(0).replace(',', '').astype(float)
df_GL['จำนวนเงินเครดิต'] = df_GL['จำนวนเงินเครดิต'].fillna(0).str.replace(',', '').astype(float)
df_GL['จำนวนเงินเดบิต'] = df_GL['จำนวนเงินเดบิต'].fillna(0).str.replace(',', '').astype(float)
# print(df_coding.head())

### Dash Opor ###
def add_commas(x):
    return f"{x:,.2f}"
def percent_decimal_2(x):
    return f"{x: .2f}%"


# Table Sum ถอนเงิน #
Bank_ถอนเงิน_amount = df_coding['ถอนเงิน'].sum()
GL_ถอนเงิน_amount = df_GL['จำนวนเงินเครดิต'].sum()
Diff_ถอนเงิน_amount = df_coding['ถอนเงิน'].sum() - df_GL['จำนวนเงินเครดิต'].sum()

percent_diff_ถอนเงิน = percent_decimal_2( (Diff_ถอนเงิน_amount / GL_ถอนเงิน_amount)*100 )
# print(percent_diff_ถอนเงิน)


table_Sum_ถอนเงิน = pd.DataFrame(
    np.array([
        [ "Bank_ ถอนเงิน", add_commas(Bank_ถอนเงิน_amount) ],
        [ "GL_ถอนเงิน", add_commas(GL_ถอนเงิน_amount) ],
        ["Diff", add_commas(Diff_ถอนเงิน_amount) ]
    ]), 
    columns=["Description","Amount"]
)
# print(table_Sum_ถอนเงิน.head())

' ------------------------------------------------------------------------------------------------------------------'
# Table Sum ฝากเงิน
Bank_ฝากเงิน_amount = df_coding['ฝากเงิน'].sum()
GL_ฝากเงิน_amount = df_GL['จำนวนเงินเดบิต'].sum() - df_coding[df_coding['Status'] == "Case_4: Other"]['ฝากเงิน'].sum()
Diff_ฝากเงิน_amount = Bank_ฝากเงิน_amount - GL_ฝากเงิน_amount

percent_diff_ฝากเงิน = percent_decimal_2( (Diff_ฝากเงิน_amount / GL_ฝากเงิน_amount)*100)
# print(percent_diff_ฝากเงิน)

table_Sum_ฝากเงิน = pd.DataFrame(
    np.array([
        [ "Bank_ ฝากเงิน", add_commas(Bank_ฝากเงิน_amount) ],
        [ "GL_ฝากเงิน", add_commas(GL_ฝากเงิน_amount) ],
        ["Diff", add_commas(Diff_ฝากเงิน_amount) ]
    ]), 
    columns=["Description","Amount"]
)
# print(table_Sum_ฝากเงิน.head())

# print(df_coding.columns)
# print(df_GL.columns)
' ------------------------------------------------------------------------------------------------------------------'
# Table Bank ถอนเงิน
table_bank_ถอนเงิน = df_coding[df_coding['ถอนเงิน'] != 0][['วันที่','รายการ','ถอนเงิน','Voucher','ช่องทาง','Status']]
table_bank_ถอนเงิน['ถอนเงิน'] = table_bank_ถอนเงิน['ถอนเงิน'].apply(add_commas)
# print(table_bank_ถอนเงิน.head())
' ----------------------------------------------------------- '
# Table GL ถอนเงิน
table_GL_ถอนเงิน = df_GL[df_GL['จำนวนเงินเครดิต'] != 0][['วันที่','เอกสาร #', 'จำนวนเงินเครดิต','ร า ย ก า ร']]
table_GL_ถอนเงิน['จำนวนเงินเครดิต'] = table_GL_ถอนเงิน['จำนวนเงินเครดิต'].apply(add_commas)
# print(table_GL_ถอนเงิน)
' ----------------------------------------------------------- '
# Table Diff ถอนเงิน
a = df_coding[df_coding['ถอนเงิน'] != 0][['วันที่','รายการ','ถอนเงิน','Voucher','ช่องทาง','Status']]
b = df_GL[df_GL['จำนวนเงินเครดิต'] != 0][['วันที่','เอกสาร #', 'จำนวนเงินเครดิต','ร า ย ก า ร']]
b = b.rename(columns={'เอกสาร #': "Voucher",'จำนวนเงินเครดิต' : "Amount", 'ร า ย ก า ร' : "Description"})
c = pd.merge(a,b, how="outer", on=["Voucher"])
c['Status'] = c['Status'].fillna('Case_4: Other')
c = c[(c['Status'] == "Case_4: Other")].reset_index(drop=True)

# if (Diff_ถอนเงิน_amount < 0):
#     c['Amount'] = -(c['Amount'].astype(float))
# elif (Diff_ถอนเงิน_amount > 0):
#     c['ถอนเงิน'] = -(c['ถอนเงิน'].astype(float))
# elif (Diff_ถอนเงิน_amount == 0):
#     print('Hi')

c['วันที่_y'] = c['วันที่_y'].fillna(c['วันที่_x'])
c['Amount'] = c['Amount'].fillna(c['ถอนเงิน'])
c['Description'] = c['Description'].fillna(c['ช่องทาง'])
c['Status2'] = c.apply(lambda c: "Not Recorded" if pd.isna(c['Voucher']) else "Not Paid", axis=1)

table_diff_ถอนเงิน = c[['วันที่_y','Voucher','Amount','Status','Status2','Description']]
table_diff_ถอนเงิน = table_diff_ถอนเงิน.rename(columns={'วันที่_y': "Date"})
# table_diff_ถอนเงิน['Amount'] = table_diff_ถอนเงิน['Amount'].apply(add_commas)

# print(table_diff_ถอนเงิน)

' ------------------------------------------------------------------------------------------------------------------'

# Table Bank ฝากเงิน
table_bank_ฝากเงิน = df_coding[df_coding['ฝากเงิน'] != 0][['วันที่','รายการ','ฝากเงิน','Voucher','ช่องทาง','Status']]
table_bank_ฝากเงิน['ฝากเงิน'] = table_bank_ฝากเงิน['ฝากเงิน'].apply(add_commas)
# print(table_bank_ฝากเงิน.head())
' ----------------------------------------------------------- '
# Table GL ฝากเงิน
table_GL_ฝากเงิน = df_GL[df_GL['จำนวนเงินเดบิต'] != 0][['วันที่','เอกสาร #', 'จำนวนเงินเดบิต','ร า ย ก า ร']]
table_GL_ฝากเงิน['จำนวนเงินเดบิต'] = table_GL_ฝากเงิน['จำนวนเงินเดบิต'].apply(add_commas)

# print(table_GL_ฝากเงิน)
' ----------------------------------------------------------- '
# Table Diff ฝากเงิน
d = df_coding[df_coding['ฝากเงิน'] != 0][['วันที่','รายการ','ฝากเงิน','Voucher','ช่องทาง','Status']]
e = df_GL[df_GL['จำนวนเงินเดบิต'] != 0][['วันที่','เอกสาร #', 'จำนวนเงินเดบิต','ร า ย ก า ร']]
e = e.rename(columns={'เอกสาร #': "Voucher",'จำนวนเงินเดบิต' : "Amount", 'ร า ย ก า ร' : "Description"})

f = pd.merge(d,e, how="outer", on=["Voucher"])

f['Status'] = f['Status'].fillna('Case_4: Other')
f = f[(f['Status'] == "Case_4: Other")].reset_index(drop=True)
# print(f)

if (Diff_ฝากเงิน_amount < 0):
    f['ฝากเงิน'] = -(f['ฝากเงิน'].astype(float))
elif (Diff_ฝากเงิน_amount > 0):
    f['Amount'] = -(f['Amount'].astype(float))
elif (Diff_ฝากเงิน_amount == 0):
    print('Hi')

# print(f)
f['วันที่_y'] = f['วันที่_y'].fillna(f['วันที่_x'])
f['Amount'] = f['Amount'].fillna(f['ฝากเงิน'])
f['Description'] = f['Description'].fillna(f['ช่องทาง'])
f['Status2'] = f.apply(lambda f: "Not Recorded" if pd.isna(f['Voucher']) else "Not Received", axis=1)

table_diff_ฝากเงิน = f[['วันที่_y','Voucher','Amount','Status','Status2','Description']]
table_diff_ฝากเงิน = table_diff_ฝากเงิน.rename(columns={'วันที่_y': "Date"})
# table_diff_ฝากเงิน['Amount'] = table_diff_ฝากเงิน['Amount'].apply(add_commas)
# print(table_diff_ฝากเงิน)
' ----------------------------------------------------------- '

## Pie Chart ###
color_pie = ['#344762','#486186','#6582ac','#8ea8cc','#afc2dd','#d2ddec','#ecf0f7','#f7f8fb']

bank_data = {
    "Classified Bank": df_coding['Classified Bank'].value_counts().index.tolist(),
    "COUNTA of รายการ": df_coding['Classified Bank'].value_counts().tolist()
}

# Data for label classifications
label_data = {
    "Classified Label": df_coding['Classified Label'].value_counts().index.tolist(),
    "COUNTA of รายการ": df_coding['Classified Label'].value_counts().tolist()
}

# print(df_coding['Classified Label'].value_counts().index.tolist())
# print(df_coding['Classified Bank'].value_counts().index.tolist())
# print(df_coding['Classified Bank'].value_counts().tolist())
# print(df_coding['Classified Label'].value_counts().tolist())
# print(bank_data)
# print(table_GL_ฝากเงิน.to_dict('records'))

# Create first pie chart for bank classifications
fig1 = px.pie(
    pd.DataFrame(bank_data),
    names="Classified Bank",
    values="COUNTA of รายการ",
    title="<b> Bank Classification </b>",
    color_discrete_sequence=color_pie
)

fig2 = px.pie(
    pd.DataFrame(label_data),
    names="Classified Label",
    values="COUNTA of รายการ",
    title="<b> Label Classification </b>",
    color_discrete_sequence=color_pie
)

## Reaname column in raw_data before show the dashboard
table_GL_ฝากเงิน = table_GL_ฝากเงิน.rename(columns={'เอกสาร #': "Voucher",'จำนวนเงินเดบิต' : "Amount", 'ร า ย ก า ร' : "Description", "วันที่" : "Date"})
table_GL_ถอนเงิน = table_GL_ถอนเงิน.rename(columns={'เอกสาร #': "Voucher",'จำนวนเงินเครดิต' : "Amount", 'ร า ย ก า ร' : "Description", "วันที่" : "Date"})

' ------------------------------------------------------------------------------------------------------------------'



colors = {
    'background_all': '#EAD8B1',
    'background_each_graph' : '#FAEED3',
}

font_sub_header = {'font':'Arial',
                   'size' : '24px'}

# Set ขนาดของ table3
set_table3 = {
    'style_header': {'display': 'fix',
        'backgroundColor': "#2B5278",
        'color' : 'white',
        'fontWeight': 'bold',
        'border': 'none',
        'border-bottom': '1px solid #d9d9d9',
        'text-align' : "center"},
    'fixed_rows': {'headers': True},
    'style_table': {'height': 200, 'overflowX': 'auto'},  # Height uses scroll below, overflowX uses scroll left-right
    'editable': True,
    'filter_action': 'native',
    'sort_action': 'native',
    'sort_mode': 'multi',
    'column_selectable': 'single',
    'selected_columns': [],
    'page_action': 'none',
    'page_current': 0,
    'page_size': 10,
    'style_data' : {'color': 'black',
        'backgroundColor': '#FCF4E1',
        'border': 'none',
        'border-bottom': '1px solid #d9d9d9'},
    'style_filter': {'color': 'black',
        'backgroundColor': '#FCF4E1',
        'border': 'none',
        'border-bottom': '3px solid #d9d9d9'},
}

set_ระยะขอบ_table3 = {"margin": 20,
                'width': 'auto'}

set_ความกว้าง_table3 = {
    'minWidth': '70px', 'width': '70px', 'maxWidth': '180px',
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'font_size': '16px',
}

set_style_header_table3 = {
'font-family': font_sub_header['font'],
'font-size' : font_sub_header['size'],
'margin' : '5px 0px 10px 0px',
'color' : 'black',
'font-weight' : 'bolder'}


### Dash ###


app = Dash(__name__)

from dash import html

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body style="background-color: #EAD8B1">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


app.layout = html.Div(
    style={'backgroundColor': colors['background_all']}, children=
    [
        html.Div(
            [
                html.H1("Bank Statement Control Dashboard", 
                        style= {'color' : "#A52E45", 
                                'font-family': 'fantasy',
                                'font-size': '60px',
                                'letter-spacing' : '2px',
                                'margin' : '0px 2px 20px 0px' })
            ],
            style= {"margin" : 20, 'width': "100%"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div([
                                html.H4("Summary Withdraw", style= {
                                    'font-family': font_sub_header['font'],
                                    'font-size' : font_sub_header['size'],
                                    'margin' : '5px 0px 10px 0px'
                                    }
                                ),
                                dash_table.DataTable(
                                    data = table_Sum_ถอนเงิน.to_dict('records'), 
                                    columns = [{"name": i, "id": i} for i in table_Sum_ถอนเงิน.columns],
                                    id='table1',
                                    style_header= {'display': 'fix',
                                    'backgroundColor': "#2B5278",
                                        'color' : 'white',
                                        'fontWeight': 'bold',
                                        'border': 'none',
                                        'border-bottom': '1px solid #d9d9d9',
                                        'text-align' : "center"},
                                    style_data={'color': 'black',
                                        'backgroundColor': '#FCF4E1',
                                        'border': 'none',
                                        'border-bottom': '1px solid #d9d9d9'},
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': c},
                                            'textAlign': 'left'
                                        } for c in ['Description']
                                    ],
                                    style_cell= {
                                        'font_size': '16px',
                                    },
                                )
                            ],
                             style={
                                 'padding' : '0px 30px 20px 20px' 
                                },
                        ),
                        html.Div([
                            html.Div(
                                className='scorecard-item',
                                style={'display': 'grid', 'placeItems': 'center'},
                                children=[
                                html.H4(f'% Diff of Withdraw',
                                    style= {
                                        'font-family': font_sub_header['font'],
                                        'font-size' : font_sub_header['size'],
                                        'margin' : '30px 0px 0px 0px',
                                        'color' : '#2B5378',
                                        'font-weight' : 'bolder'}
                                ),
                                html.P(str(percent_diff_ถอนเงิน),  
                                       style= {
                                        'font-family': font_sub_header['font'],
                                        'font-size' : font_sub_header['size'],
                                        'color' : "#A52E45",
                                        'font-weight' : 'bolder',
                                        }
                                    )
                                ]
                            ),
                        ],
                            style={"border": "0px solid black", 
                                   "border-radius": "10px", 
                                   "box-shadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",
                                    'padding' : '0px 0px 0px 0px',
                                    'background-color': '#F8EDD8',
                                    'margin' : '20px 0px 0px 10px'  
                                }
                        )
                    ],
                    style= {"margin" : 0,'display': 'inline-block', 'width' : '27%'}
                ),
                html.Div( 
                    [
                        html.Div([
                                html.H4("Summary Deposit", style= {
                                    'font-family': font_sub_header['font'],
                                    'font-size' : font_sub_header['size'],
                                    'margin' : '5px 0px 10px 0px'
                                    }
                                ),
                                dash_table.DataTable(
                                    data = table_Sum_ฝากเงิน.to_dict('records'), 
                                    columns = [{"name": i, "id": i} for i in table_Sum_ฝากเงิน.columns],
                                    id='table2',
                                    style_header= {'display': 'fix',
                                    'backgroundColor': "#2B5278",
                                        'color' : 'white',
                                        'fontWeight': 'bold',
                                        'border': 'none',
                                        'border-bottom': '1px solid #d9d9d9',
                                        'text-align' : "center"},
                                    style_data={'color': 'black',
                                        'backgroundColor': '#FCF4E1',
                                        'border': 'none',
                                        'border-bottom': '1px solid #d9d9d9'},
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': c},
                                            'textAlign': 'left'
                                        } for c in ['Description']
                                    ],
                                    style_cell= {
                                        'font_size': '16px',
                                    }
                                ),
                            ],
                            style={
                                'padding' : '0px 30px 20px 20px' 
                                    },
                        ),

                        html.Div([
                                html.Div(
                                    className='scorecard-item',
                                    style={'display': 'grid', 'placeItems': 'center'},
                                    children=[
                                    html.H4(f"% Diff of Deposit",
                                        style= {
                                            'font-family': font_sub_header['font'],
                                            'font-size' : font_sub_header['size'],
                                            'margin' : '30px 0px 0px 0px',
                                            'color' : '#2B5378',
                                            'font-weight' : 'bolder'}
                                    ),
                                    html.P(str(percent_diff_ฝากเงิน),
                                        style= {
                                            'font-family': font_sub_header['font'],
                                            'font-size' : font_sub_header['size'],
                                            'color' : "#388E3C",
                                            'font-weight' : 'bolder',
                                        }
                                        )
                                    ]
                                ),
                            ],
                                style={"border": "0px solid black", 
                                   "border-radius": "10px", 
                                   "box-shadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",
                                    'padding' : '0px 0px 0px 0px',
                                    'background-color': '#F8EDD8',
                                    'margin' : '20px 0px 0px 10px'  
                                }
                        ),     
                    ], 
                        style= {"margin" : -2,'display': 'inline-block', 'width' : '27%'}
                ),
                html.Div(
                            [
                                dcc.Graph(
                                        id='bank-pie-chart',
                                        figure=fig1,
                                    ),
                            ], style={"margin" : 20,'width': '35%','display': 'inline-block'}
                        ),
                html.Div(
                    [
                        dcc.Graph(
                            id='label-pie-chart',
                            figure=fig2,
                        ),
                    ], style={"margin" : 20,'width': '35%','display': 'inline-block'}
                ),
            ], style={'display': 'flex'}),
        html.Div(id='table3-container', style={"border": "1px solid black", 
                                               "border-radius": "10px", 
                                               "box-shadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",
                                               "margin" : "-20px 0px 50px 0px"
                                               }), # Dash Diff Detailed
    ]
)

@app.callback(
    Output(component_id='table3-container', component_property='children'),
    [Input(component_id='table1', component_property='active_cell'),
     Input(component_id='table2', component_property='active_cell')],
)
def update_table3(active_cell_table1, active_cell_table2):
    if callback_context.triggered:
        ctx_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        
        if ctx_id == 'table1' and active_cell_table1:
            row = active_cell_table1['row']
            col = active_cell_table1['column_id']
            if row == 0 and col == 'Amount':
                cell_value = table_Sum_ถอนเงิน.loc[row, col]
                return [
                    html.Div(
                        [
                            html.H2(f"Bank Statement - Withdrawal Transaction",
                                    style = set_style_header_table3),
                            dash_table.DataTable(
                                id='table3',
                                columns=[{"name": i, "id": i} for i in table_bank_ถอนเงิน.columns],
                                data=table_bank_ถอนเงิน.to_dict('records'),
                                style_cell= set_ความกว้าง_table3,
                                **set_table3
                            ),
                        ], 
                        style= set_ระยะขอบ_table3
                    )
                ]
            elif row == 1 and col == 'Amount':
                cell_value = table_Sum_ถอนเงิน.loc[row, col]
                return [
                    html.Div(
                        [
                            html.H2(f"General Ledger - Withdrawal", 
                                    style = set_style_header_table3),
                            dash_table.DataTable(
                                id='table3',
                                columns=[{"name": i, "id": i} for i in table_GL_ถอนเงิน.columns],
                                data=table_GL_ถอนเงิน.to_dict('records'),
                                style_cell= set_ความกว้าง_table3,
                                **set_table3
                            ),
                        ], 
                        style= set_ระยะขอบ_table3
                    )
                ]
            elif row == 2 and col == 'Amount':
                cell_value = table_Sum_ถอนเงิน.loc[row, col]
                return [
                    html.Div(
                        [
                            html.H2(f"Diff Detail Withdrawal",
                                    style = set_style_header_table3),
                            dash_table.DataTable(
                                id='table3',
                                columns=[{"name": i, "id": i} for i in table_diff_ถอนเงิน.columns],
                                data=table_diff_ถอนเงิน.to_dict('records'),
                                style_cell= set_ความกว้าง_table3,
                                **set_table3,
                            ),
                        ], 
                        style = set_ระยะขอบ_table3
                    )
                ]
        elif ctx_id == 'table2' and active_cell_table2:
            row = active_cell_table2['row']
            col = active_cell_table2['column_id']
            if row == 0 and col == 'Amount':
                cell_value = table_Sum_ฝากเงิน.loc[row, col]
                return [
                        html.Div(
                            [
                                html.H2(f"Bank Statement - Deposit Transaction",
                                        style = set_style_header_table3),
                                dash_table.DataTable(
                                    id='table3',
                                    columns=[{"name": i, "id": i} for i in table_bank_ฝากเงิน.columns],
                                    data=table_bank_ฝากเงิน.to_dict('records'),
                                    style_cell= set_ความกว้าง_table3,
                                    **set_table3
                                ),
                            ],
                            style = set_ระยะขอบ_table3
                        )
                ]
            elif row == 1 and col == 'Amount':
                cell_value = table_Sum_ฝากเงิน.loc[row, col]
                return [
                    html.Div(
                        [
                            html.H2(f"General Ledger - Deposit",
                                    style = set_style_header_table3),
                            dash_table.DataTable(
                                id='table3',
                                columns=[{"name": i, "id": i} for i in table_GL_ฝากเงิน.columns],
                                data=table_GL_ฝากเงิน.to_dict('records'),
                                style_cell= set_ความกว้าง_table3,
                                **set_table3
                            ),
                        ], 
                        style = set_ระยะขอบ_table3
                    )
                ]
            elif row == 2 and col == 'Amount':
                cell_value = table_Sum_ฝากเงิน.loc[row, col]
                return [
                    html.Div(
                        [
                            html.H2(f"Diff Detail Deposit",
                                    style = set_style_header_table3),
                            dash_table.DataTable(
                                id='table3',
                                columns=[{"name": i, "id": i} for i in table_diff_ฝากเงิน.columns],
                                data=table_diff_ฝากเงิน.to_dict('records'),
                                style_cell= set_ความกว้าง_table3,
                                **set_table3
                            ),
                        ], 
                        style = set_ระยะขอบ_table3
                    )
                ]

    # If no cell is clicked or conditions are not met, set initial content
    return [
        html.Div(
            [
                html.H2("Bank Statement", 
                        style = set_style_header_table3),
                dash_table.DataTable(
                    id='table3',
                    columns=[{"name": i, "id": i} for i in df_coding.columns],
                    data=df_coding.to_dict('records'),
                    style_cell= set_ความกว้าง_table3,
                    **set_table3, style_data_conditional= [{
                        'if': {'filter_query': '{Status} eq "Case_4: Other"'},
                        'backgroundColor': '#BE7492',
                        'color': 'white'
                    }],
                )
            ], 
            style = set_ระยะขอบ_table3
        )  # Set the width of the div containing table3
    ]

# update layout graph

fig1.update_layout(
        plot_bgcolor=colors['background_all'],
        paper_bgcolor=colors['background_all'],
        font=dict(color= 'black'),
        title_font_family = font_sub_header['font'],
        title_font_size = int(font_sub_header['size'].split('px')[0]),
    )


fig2.update_layout(
        plot_bgcolor=colors['background_all'],
        paper_bgcolor=colors['background_all'],
        font=dict(color= 'black'),
        title_font_family = font_sub_header['font'],
        title_font_size = int(font_sub_header['size'].split('px')[0])
    )

if __name__ == '__main__':
    app.run_server(debug=True)




# print(f"table_Sum_ถอนเงิน = {table_Sum_ถอนเงิน.columns}")
# print(f"table_Sum_ฝากเงิน = {table_Sum_ฝากเงิน.columns}")
# print(f"table_bank_ถอนเงิน = {table_bank_ถอนเงิน.columns}")
# print(f"table_GL_ถอนเงิน = {table_GL_ถอนเงิน.columns}")
# print(f"table_diff_ถอนเงิน = {table_diff_ถอนเงิน.columns}")
# print(f"table_bank_ฝากเงิน = {table_bank_ฝากเงิน.columns}")
# print(f"table_GL_ฝากเงิน = {table_GL_ฝากเงิน.columns}")
# print(f"table_diff_ฝากเงิน = {table_diff_ฝากเงิน.columns}")







