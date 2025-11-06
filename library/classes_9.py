class Budget:
    def __init__(self, expense_cat):
        self.expense_cat = expense_cat
        self.expenses_type = []
        self.expenses_cost = []

    def add_expense(self):
        while True:
            try:
                count = int(input(f"Enter the number of expenses you want to input for {self.expense_cat}: "))
                break
            except:
                print("Invalid input. Please enter an integer value.")
                continue
        
        print(f"Enter expenses in 'type cost' format. For example: '{self.expense_cat} 50.5'")
        for i in range(count):   
            while True:
                try:
                    expense_type, expense_cost = input(f"Enter expense #{i+1} for {self.expense_cat}: ").split()
                    self.expenses_type.append(expense_type)
                    self.expenses_cost.append(float(expense_cost))
                    break
                except:
                    print(f"Invalid input format. Please enter in 'type cost' format. For example: '{self.expense_cat} 50.5'")
                    continue

    def get_expenses(self):
        total = sum(self.expenses_cost)
        print(f"Total expenses for {self.expense_cat}: ${total:.2f}")
        return total
    
    def get_expense_details(self):
        print(f"Expense details for {self.expense_cat}:")
        for expense in zip(self.expenses_type, self.expenses_cost):
            print(f" - {expense[0]}: ${expense[1]:.2f}")
    
    

    


    