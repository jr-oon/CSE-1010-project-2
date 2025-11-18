class Budget:
    """
    Tracks expenses across categories.
    data = { "Grocery": [(name, cost), ...], "Car": [(name, cost), ...] }
    """
    def __init__(self, categories: list[str]):
        self.categories = list(categories)
        self.data: dict[str, list[tuple[str, float]]] = {c: [] for c in self.categories}

    def add_expense(self, category: str, expense_name: str, expense_cost: float) -> None:
        if category not in self.data:
            # If a new category somehow appears, initialize it.
            self.data[category] = []
        self.data[category].append((expense_name, float(expense_cost)))

    def total(self) -> float:
        return sum(cost for items in self.data.values() for _, cost in items)

    def total_by_category(self) -> dict[str, float]:
        return {c: sum(cost for _, cost in self.data.get(c, [])) for c in self.data}

    def items_by_category(self, category: str) -> list[tuple[str, float]]:
        return list(self.data.get(category, []))
