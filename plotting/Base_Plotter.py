import os
import sys
import dash_bootstrap_components as dbc
import plotly.offline as offline
from dash import Input, Output, State, ctx, dcc, html

# insert package path to get the utils components
sys.path.insert(0, r'talmin')
from utils.Base_Components import *

            
class Base_Fig:
    def __init__(self,save_path):
        self.save_path=None
        def set_save_path(path:os.path.normpath):
            """_summary_

            Args:
                path (os.path.normpath)): set global save path
            """
            self.save_path=path
        def get_save_path():
            return save_path 
        
        def save(fig, title,auto_open=False):
            """
            Save the Plotly figure as an image file

            Args:
                filename (str): Path and Name of the Graph to be saved
                auto_open (bool, optional): Open the html_file in the default browser. Defaults to False.
            """
            filename=title+'.html'
            os.makedirs(os.path.dirname(filename),exist_ok=True)
            offline.plot(fig,filename=filename,auto_open=auto_open,include_plotlyjs='cdn',config=
                        dict(displaylogo=False, toImageButtonOptions=dict(format= 'svg'),
                        modeBarButtonsToAdd=['drawline',
                                            'drawopenpath',  
                                            'drawclosedpath',
                                            'drawcircle',
                                            'drawrect',
                                            'eraseshape'
                                        ]))

           

