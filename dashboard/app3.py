from shiny import reactive
from shiny.express import input, render, ui
#from shinywidgets import render_plotly
import matplotlib.pyplot as plt
from shared import app_dir, data, SourceRepositories, PublishersUI



from makeplot1 import plot_publisher_repo_by_year

ui.page_opts(title="Researchdata.se dashboard", fillable=True)

with ui.sidebar():
    ui.input_selectize(
        "publisher", "Select principal:", PublishersUI)
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
