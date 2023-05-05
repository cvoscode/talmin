import dash_bootstrap_components as dbc

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
    return dbc.Select(id=id,options=options,value=value)
