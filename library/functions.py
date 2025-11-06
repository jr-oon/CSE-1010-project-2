def calc_balance(income, expenses):
    balance = income - expenses
    return balance

def financial_status(balance):
    if balance > 0:
        print("Great! You are saving money")
    elif balance == 0:
        print("You are breaking even.")
    else:
        print("**WARNING** You are overspending!")

def expense_collect():
    count = int(input("Enter the number of expenses you want to input: "))
    expenses = []
    for i in range(count):
       expense = float(input(f"Enter expense {i+1}: "))
       expenses.append(expense)

    return expenses
