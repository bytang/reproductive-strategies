from mesa.discrete_space import CellAgent

class Animal(CellAgent):
    """The base animal class."""

    def __init__(self, model, energy=10, cell=None):
        """Initialize an animal.

        Args:
            model: Model instance
            energy: Starting amount of energy
            cell: Cell in which the animal starts
        """
        super().__init__(model)
        self.energy = self.random.normalvariate(energy, energy/10)
        self.cell = cell
        self.fitness = self.random.normalvariate()

    def feed(self):
        self.energy += self.random.normalvariate(self.fitness)

    def step(self):
        """Execute one step of the animal's behavior."""
        # Move to random neighboring cell
        # self.move()

        self.energy -= 1


        # Handle death and feeding
        if self.energy <= 0:
            self.remove()
        else:
            self.feed()

class Bearer(Animal):
    """"""

class Giver(Animal):
    """"""