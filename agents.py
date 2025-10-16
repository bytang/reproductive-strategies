from mesa.discrete_space import CellAgent

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
        self.fitness = fitness if fitness is not None else self.random.normalvariate()
        self.parents = parents

    def feed(self):
        if self.fitness > self.random.normalvariate(self.model.habitability):
            self.energy = min(self.energy + 2, self.energy_max)

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
        self.mate()
        self.move()

        # Handle death and feeding
        if self.energy <= 0:
            self.remove()
        else:
            self.lifetime += 1
            if self.lifetime > 30:
                self.adult = True
            if self.adult:
                self.feed()

class Carrier(Animal):
    """"""
    def __init__(self, model, parents=None, fitness=None, adult=True, energy=10, cell=None):
        super().__init__(model, parents, fitness, adult, energy, cell)
        self.carrying = False
        self.carry = {
            'time': 0,
            'fitness': 0,
            'energy_reserve': 0,
            'mature': 270,
            'parents': None
        }
        self.role = 'carrier'
    
    def mate(self):
        if not self.carrying:
            choices = [obj for obj in self.cell.agents if isinstance(obj, Giver)]
            if len(choices):
                if self.model.choosy:
                    partner = choices[0]
                    for choice in choices:
                        if choice.fitness > partner.fitness:
                            partner = choice
                else:
                    partner = self.random.choice(choices)
                crossover_ratio = self.model.dist.cdf(self.random.normalvariate())
                self.carrying = True
                if self.model.mutation and self.random.uniform(0, 1) < 0.05:
                    self.carry['fitness'] = self.random.normalvariate()
                else:
                    self.carry['fitness'] = crossover_ratio * self.fitness + (1 - crossover_ratio) * partner.fitness
                self.carry['time'] = 0
                self.carry['energy_reserve'] = 0
                self.carry['parents'] = [self.unique_id, partner.unique_id]

    def metabolism(self):
        self.energy -= 1 + (0.5 if self.carrying else 0)
        if self.carrying:
            if self.carry['time'] < self.carry['mature']:
                self.carry['time'] += 1
                self.carry['energy_reserve'] += 0.25
            else:
                self.carrying = False
                role = self.random.choice(['carrier', 'giver'])
                if role == 'carrier':
                    Carrier(
                        self.model,
                        self.carry['parents'],
                        self.carry['fitness'],
                        False,
                        self.carry['energy_reserve'],
                        self.cell
                    )
                else:
                    Giver(
                        self.model,
                        self.carry['parents'],
                        self.carry['fitness'],
                        False,
                        self.carry['energy_reserve'],
                        self.cell
                    )

class Giver(Animal):
    """"""
    def __init__(self, model, parents=None, fitness=None, adult=True, energy=10, cell=None):
        super().__init__(model, parents, fitness, adult, energy, cell)
        self.role = 'giver'
    
    def metabolism(self):
        self.energy -= 1