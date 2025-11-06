import os
from library import classes_9
from library import functions
os.system('cls' if os.name == 'nt' else 'clear')


print("Hey there, this is BudgetBuddy! Your personal Budgeting Assistant")
name = input("Enter your name: ")
print(f"Hey, {name} this is BudgetBuddy! Your personal Budgeting Assistant")

income = float(input("Enter your monthly income: "))
total_expenses = []

grocery = classes_9.Budget("Grocery")
grocery.add_expense()
total_expenses.append(grocery.get_expenses())

car = classes_9.Budget("Car")
car.add_expense()
total_expenses.append(car.get_expenses())


balance = functions.calc_balance(income, sum(total_expenses))
functions.financial_status(balance)


grocery.get_expense_details()
car.get_expense_details()