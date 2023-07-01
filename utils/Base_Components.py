import sys

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import polars as pl
sys.path.insert(0, r'talmin')
from utils.polars_addons import detect_column_types
from dash import dcc,Input,Output,State,ctx


def create_Button(id:str,color:str,children):
    """Create a standard Button for the app.

    Args:
        id (str): dash.id
        color (str): Options: primary, secondary, success, info, warning, danger, link
        children (dash component): Anything   
    """
    return dbc.Button(id=id, color=color,children=children,className="ml-auto",style={'white-space': 'nowrap'})

def create_Text_Input(id:str,placeholder:str,value=None):
    """create a standard text input for the app.

    Args:
        id (str): dash.id
        placeholder (str): placeholder text if nothing is inputted
        value (str): an intial value to be shown
    """
    return dbc.Input(id=id,type='text',placeholder=placeholder,value=value,debounce=True,className="ml-auto",autocomplete=True)

def create_Numeric_Input(id:str,placeholder:str=None,value=None,step=None,min=None,max=None):
    """create a standard text input for the app.

    Args:
        id (str): dash.id
        placeholder (str): placeholder text if nothing is inputted
        value (str): an intial value to be shown
    """
    return dbc.Input(id=id,type='number',placeholder=placeholder,value=value,debounce=True,className="ml-auto",autocomplete=True,step=step,min=min,max=max)

def create_Tooltip(tip:str,target:str):
    """Creates a tooltip for a target component

    Args:
        tip (str): dash.id
        target (str): dash.id
    """

    return dbc.Tooltip(tip,target=target,placement='top',className="ml-auto")

def create_Toast(children,header:str,icon:str):
    """creates a standard toast for the app

    Args:
        children (anything): _description_
        header (str) : Header for the Toast
        icon (str): Options: "primary", "secondary", "success", "warning", "danger", "info", "light" or "dark"

    Returns:
        _type_: _description_
    """
    return dbc.Toast(children=children,header=header,duration=5000,is_open=True,dismissable=True,icon=icon,style={"position": "fixed", "top": 66, "right": 10, "width": 350})

def create_dropdown(id:str,options:list,value):
    """create a dropdown menu without multiselection

    Args:
        id (str): dash.id
        options (list): can be a list of dict or just a list, hold the avaliable options
        value (): is the default value of the component

    Returns:
        _type_: _description_
    """
    return dcc.Dropdown(options=options,id=id,value=value, className="dbc")
#dbc.Select(id=id,options=options,value=value)

def create_dropdown_paging(id:str,options:list,value,name,multi):
    return dbc.InputGroup([dbc.InputGroupText(name,style=dict(width='120px')),dcc.Dropdown(id=id,options=options,value=value,multi=multi,className="dbc",style=dict(width='120px')),dbc.Button(id=f'{id}-prev',children='<<'),dbc.Button(id=f'{id}-next',children='>>')])
def create_dropdown_paging_callback(id,app):
    @app.callback(Output(id,'value'),
                  Input(f'{id}-prev','n_clicks'),
                  Input(f'{id}-next','n_clicks'),
                  State(id,'value'),
                  State(id,'options'),
                  prevent_inital_callback=True
                  )
    def next_prev(prev,next,value,options):
        if value:
            index=options.index(value)
            if ctx.triggered_id==f'{id}-next':
                index=index+1
                if index>=len(options):
                    index=0
                return options[index]
            if ctx.triggered_id==f'{id}-prev':
                index=index-1
                if index<0:
                    index=len(options)-1
                return options[index]
            


def create_table(id:str,df:pl.DataFrame):
    numeric_cols,temporal_cols,nested_cols,discrete_cols=detect_column_types(df)
    columnDefs=[{"field":i,"filter": "agNumberColumnFilter" } for i in numeric_cols]
    columnDefs.extend([{"field":i,"filter": "agDateColumnFilter" } for i in temporal_cols])
    columnDefs.extend([{"field":i,"filter": "agTextColumnFilter" } for i in nested_cols+discrete_cols])
    return dag.AgGrid(
    id=id,
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth":125},
    columnSize="sizeToFit",
    columnDefs=columnDefs,
    rowData=df.to_dicts(),
    dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
    )