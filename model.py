"""
Reproductive Fitness Model
=====================

Animals
"""

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from agents import Animal

class Fitness(Model):
    """A simple model of an ecosystem where agents eat and die.

    All agents begin with eight units of energy, and each time step agents gain energy based on their fitness.

    Attributes:
        num_agents (int): Number of agents in the model
        grid (MultiGrid): The space in which agents move
        running (bool): Whether the model should continue running
        datacollector (DataCollector): Collects and stores model data
    """

    def __init__(self, n=100, width=10, height=10, seed=None):
        """Initialize the model.

        Args:
            n (int, optional): Number of agents. Defaults to 100.
            width (int, optional): Grid width. Defaults to 10.
            height (int, optional): Grid height. Defaults to 10.
            seed (int, optional): Random seed. Defaults to None.
        """
        super().__init__(seed=seed)

        self.num_agents = n
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        # Set up data collection
        self.datacollector = DataCollector(
            agent_reporters={"Energy": "energy", "Fitness": "fitness"},
        )
        Animal.create_agents(
            self,
            self.num_agents,
            energy=25,
            cell=self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")  # Activate all agents in random order
        self.datacollector.collect(self)  # Collect data
