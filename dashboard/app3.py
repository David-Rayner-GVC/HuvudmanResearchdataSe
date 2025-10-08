from shiny import reactive
from shiny.express import input, render, ui
#from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from shared import app_dir, data, SourceRepositories, Publishers


# Import from the common folder
import os, sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
common_path = Path(__file__).resolve().parent.parent / "common"
# Add to sys.path if not already there
if str(common_path) not in sys.path:
    sys.path.insert(0, str(common_path))  # insert(0) so it takes precedence
from makeplot1 import plot_publisher_repo_by_year

ui.page_opts(title="Researchdata.se dashboard", fillable=True)

with ui.sidebar():
    ui.input_selectize(
        "publisher", "Select variable", Publishers)
    #ui.input_numeric("bins", "Number of bins", 30)

@reactive.calc
def df():
    return data[YearPublished]

# @render_plotly
# def hist():
#     import plotly.express as px
#     p = px.histogram(df(), nbins=input.bins())
#     p.layout.update(showlegend=False)
#     return p
        
with ui.card(full_screen=True):
  @render.plot(alt="A histogram")  
  def plot():  
      fig = plot_publisher_repo_by_year(input.publisher(), data) 
      return fig
