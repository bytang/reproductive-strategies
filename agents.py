from mesa.discrete_space import CellAgent
from scipy.stats import truncnorm
from itertools import chain

class Animal(CellAgent):
    """The base animal class."""

    def __init__(self, model, parents=None, fitness=None, adult=True, energy=10, cell=None):
        """Initialize an animal.

        Args:
            model: Model instance
            energy: Starting amount of energy
            cell: Cell in which the animal starts
        """
        super().__init__(model)
        self.energy = self.random.normalvariate(energy, energy/10)
        self.energy_max = 50
        self.cell = cell
        self.adult = adult
        self.lifetime = 0
        self.fitness = fitness if fitness is not None else truncnorm.rvs(-2, 2)
        self.parents = parents

    def feed(self):
        if self.adult:
            if self.fitness - self.lifetime/1096 > self.random.normalvariate(self.model.habitability):
                self.energy = min(self.energy + 2, self.energy_max)
        else:
            self.energy += 1

    def mate(self):
        """Abstract method to be implemented by subclasses."""
    
    def metabolism(self):
        """Abstract method to be implemented by subclasses."""

    def move(self):
        self.cell = self.cell.neighborhood.select_random_cell()

    def step(self):
        """Execute one step of the animal's behavior."""
        # Move to random neighboring cell
        self.metabolism()
        if self.adult:
            self.mate()
        self.move()

        # Handle death and feeding
        if self.energy <= 0:
            self.model.add_death(self)
            self.remove()
        else:
            self.lifetime += 1
            if self.lifetime > 300:
                self.adult = True
            self.feed()

class Carrier(Animal):
    """"""
    def __init__(self, model, parents=None, fitness=None, adult=True, strategy='none', energy=10, cell=None):
        super().__init__(model, parents, fitness, adult, energy, cell)
        self.carrying = False
        self.carry = {
            'time': 0,
            'fitness': 0,
            'energy_reserve': 0,
            'mature': 27,
            'parents': None
        }
        self.choose_timer = 0
        self.partner = None
        self.role = 'carrier'
        self.strategy = strategy
        self.model.add_birth(self)
    
    def mate(self):
        if not self.carrying and self.energy > 40:
            if self.partner is None:
                search_area = self.cell.get_neighborhood(radius=2, include_center=True)

                choices = []
                for cell in search_area:
                    choices.append([obj for obj in cell.agents if isinstance(obj, Giver)])
                choices = list(chain.from_iterable(choices))

                if len(choices):
                    if self.strategy == 'choosy':
                        partner = choices[0]
                        for choice in choices:
                            if choice.fitness > partner.fitness:
                                partner = choice
                        self.partner = partner
                    elif self.strategy == 'none':
                        self.partner = self.random.choice(choices)
            
            if self.strategy == 'choosy':
                if self.partner is not None:
                    self.choose_timer += 1
                else:
                    self.partner = None
                    self.choose_timer = 0

            if self.partner is not None and (self.strategy == 'none' or self.choose_timer > self.model.choose_delay):
                crossover_ratio = self.model.dist.cdf(self.random.normalvariate())
                self.carrying = True
                if self.model.mutation and self.random.uniform(0, 1) < 0.1:
                    self.carry['fitness'] = truncnorm.rvs(-2, 2) - max(self.lifetime - 1096, 0)/731
                else:
                    self.carry['fitness'] = (crossover_ratio * self.fitness + (1 - crossover_ratio) * self.partner.fitness) - max(self.lifetime - 1096, 0)/731
                self.carry['time'] = 0
                self.carry['energy_reserve'] = 0
                self.carry['parents'] = [self.unique_id, self.partner.unique_id]
                self.choose_timer = 0

    def metabolism(self):
        self.energy -= 1 + (0.5 if self.carrying else 0)
        if self.carrying:
            if self.carry['time'] < self.carry['mature']:
                self.carry['time'] += 1
                self.carry['energy_reserve'] += 0.25
            else:
                self.carrying = False
                self.partner = None
                role = self.random.choice(['carrier', 'giver'])
                if role == 'carrier':
                    Carrier(
                        self.model,
                        self.carry['parents'],
                        self.carry['fitness'],
                        False,
                        self.strategy,
                        self.carry['energy_reserve'],
                        self.cell
                    )
                else:
                    Giver(
                        self.model,
                        self.carry['parents'],
                        self.carry['fitness'],
                        False,
                        'none',
                        self.carry['energy_reserve'],
                        self.cell
                    )

class Giver(Animal):
    """"""
    def __init__(self, model, parents=None, fitness=None, adult=True, strategy='none', energy=10, cell=None):
        super().__init__(model, parents, fitness, adult, energy, cell)
        self.role = 'giver'
        self.partner = []
        self.strategy = strategy
        self.model.add_birth(self)
    
    def metabolism(self):
        self.energy -= 1
