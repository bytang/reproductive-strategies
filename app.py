import mesa
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

from agents import Carrier, Giver
from model import Fitness

def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
        zorder=2,
    )

    if isinstance(agent, Carrier):
        portrayal.update(("color", "red"))
    elif isinstance(agent, Giver):
        portrayal.update(("color", "cyan"))

    return portrayal


model_params = {
    "n": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "width": 10,
    "height": 10,
}

fitness_model = Fitness(n=50, width=10, height=10)

renderer = SpaceRenderer(model=fitness_model, backend="altair")
renderer.draw_structure(
    xlabel="x",
    ylabel="y",
    grid_width=2,
    grid_dash=[1],
    grid_color="black",
    grid_opacity=0.1,
    title="Fitness Model",
)
renderer.draw_agents(agent_portrayal)

def post_process(chart):
    """Customize the Altair chart after rendering."""
    chart = (
        chart.properties(
            title="Fitness Model",
            width=600,
            height=400,
        )
        .configure_axis(
            labelFontSize=12,
            titleFontSize=14,
        )
        .configure_title(fontSize=16)
    )
    return chart


renderer.post_process = post_process

page = SolaraViz(
    fitness_model,
    renderer,
    components=[],
    model_params=model_params,
    name="Fitness Model",
)

# This is required to render the visualization in a Jupyter notebook
page