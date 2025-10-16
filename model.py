"""
Reproductive Fitness Model
=====================

Animals
"""

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid
from agents import Carrier, Giver
import numpy as np
import pandas as pd
from statistics import NormalDist

def compute_avg_fitness(model):
    if len(model.agents):
        return np.average([agent.fitness for agent in model.agents])
    else:
        return pd.NA

def get_population(model):
    return len(model.agents)

def compute_habitability(model):
    return model.dist.inv_cdf(1 - min(1, model.abundance/(max(len(model.agents), 1)/len(model.grid.all_cells))) * 0.5)

class Fitness(Model):
    """A simple model of an ecosystem where agents eat, mate, and die.

    All agents begin with around 25 units of energy and each step is one day.

    Matings are random and from mating to birth is 270 days (~9 months).

    Attributes:
        num_agents (int): Number of agents in the model
        grid (MultiGrid): The space in which agents move
        running (bool): Whether the model should continue running
        datacollector (DataCollector): Collects and stores model data
    """

    def __init__(self, n=100, width=10, height=10, abundance=1, mutation=True, choosy=False, seed=None):
        """Initialize the model.

        Args:
            n (int, optional): Number of agents. Defaults to 100.
            width (int, optional): Grid width. Defaults to 10.
            height (int, optional): Grid height. Defaults to 10.
            seed (int, optional): Random seed. Defaults to None.
        """
        super().__init__(seed=seed)
        self.dist = NormalDist(0, 1)
        self.abundance = abundance
        self.mutation = mutation
        self.choosy = choosy
        self.habitability = 0
        self.num_agents = int(n/2)
        self.grid = OrthogonalMooreGrid((width, height), random=self.random)

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Avg Fitness": compute_avg_fitness,
                "Population": lambda m: len(m.agents),
                "Carriers": lambda m: len(m.agents_by_type[Carrier]),
                "Givers": lambda m: len(m.agents_by_type[Giver]),
            },
            agent_reporters={"Energy": "energy", "Fitness": "fitness", "Role": "role"}
        )
        Carrier.create_agents(
            self,
            self.num_agents,
            energy=25,
            cell=self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        Giver.create_agents(
            self,
            self.num_agents,
            energy=25,
            cell=self.random.choices(self.grid.all_cells.cells, k=self.num_agents),
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.habitability = compute_habitability(self)
        self.agents.shuffle_do("step")  # Activate all agents in random order
        self.datacollector.collect(self)  # Collect data
