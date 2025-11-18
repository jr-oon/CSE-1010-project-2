import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from library.classes import Budget
from library.functions import calc_balance, format_currency, parse_float, financial_status_msg

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BudgetBuddy")
        self.geometry("460x430")

        # Shared state
        self.user_name: str = ""
        self.monthly_income: float = 0.0

        # Categories are user-defined (default only used as fallback)
        self.categories: list[str] = []
        self.default_categories = ["Grocery", "Car"]

        # One Budget object that tracks category totals
        self.budget: Budget | None = None

        # Path to currently associated budget file (if any)
        self.budget_file_path: str | None = None

        # Container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Frames
        self.frames = {}
        for F in (WelcomeFrame, ExpenseFrame, SummaryFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(WelcomeFrame)

    def show_frame(self, frame_class):
        self.frames[frame_class].tkraise()

    def go_to_expenses(self):
        # Create Budget if needed, using the current categories
        if self.budget is None:
            if not self.categories:
                # Fallback if somehow categories weren’t set
                self.categories = list(self.default_categories)
            self.budget = Budget(categories=self.categories)

        self.frames[ExpenseFrame].refresh()
        self.show_frame(ExpenseFrame)

    def go_to_summary(self):
        # Ensure summary reflects latest totals
        self.frames[SummaryFrame].refresh()
        self.show_frame(SummaryFrame)

class WelcomeFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome to BudgetBuddy!", font=("Arial", 16)).pack(pady=10)

        # Name + income
        ttk.Label(self, text="Your name:").pack()
        self.name_entry = ttk.Entry(self)
        self.name_entry.pack(pady=4, fill="x", padx=10)

        ttk.Label(self, text="Monthly income:").pack()
        self.income_entry = ttk.Entry(self)
        self.income_entry.pack(pady=4, fill="x", padx=10)

        # Categories input
        ttk.Label(self, text="Categories (one per line):").pack(pady=(8, 2))
        self.categories_text = tk.Text(self, height=5)
        self.categories_text.pack(fill="both", padx=10, pady=(0, 4))

        # Buttons: save categories + load full budget file
        cat_btns = ttk.Frame(self)
        cat_btns.pack(pady=(2, 6))
        ttk.Button(
            cat_btns,
            text="Save Categories to File",
            command=self.save_categories
        ).grid(row=0, column=0, padx=4)
        ttk.Button(
            cat_btns,
            text="Load Budget File",
            command=self.load_budget_file
        ).grid(row=0, column=1, padx=4)

        # Message
        self.msg = ttk.Label(self, text="", foreground="red")
        self.msg.pack(pady=(2, 0))

        ttk.Button(self, text="Next", command=self.on_next).pack(pady=10)

        self.name_entry.focus()

    def get_categories_from_text(self) -> list[str]:
        raw = self.categories_text.get("1.0", "end")
        cats = [line.strip() for line in raw.splitlines() if line.strip()]
        return cats

    def on_next(self):
        name = (self.name_entry.get() or "").strip()
        income_str = (self.income_entry.get() or "").strip()

        ok, income = parse_float(income_str)
        if not ok:
            self.msg.config(text="Income must be a valid number.")
            return

        cats = self.get_categories_from_text()
        if not cats:
            cats = list(self.controller.default_categories)

        old_cats = self.controller.categories

        # Update shared state
        self.msg.config(text="")
        self.controller.user_name = name or "User"
        self.controller.monthly_income = income

        # If categories changed, reset budget and file association
        if old_cats != cats:
            self.controller.categories = cats
            self.controller.budget = None
            self.controller.budget_file_path = None
        else:
            # If there were no old categories at all, set them
            if not old_cats:
                self.controller.categories = cats

        self.controller.go_to_expenses()

    def save_categories(self):
        cats = self.get_categories_from_text()
        if not cats:
            messagebox.showwarning("No categories", "Please enter at least one category before saving.")
            return

        path = filedialog.asksaveasfilename(
            title="Save category file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(cats))
        except OSError as e:
            messagebox.showerror("Error", f"Could not write file:\n{e}")

    def load_budget_file(self):
        path = filedialog.askopenfilename(
            title="Select budget file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f]
        except OSError as e:
            messagebox.showerror("Error", f"Could not read budget file:\n{e}")
            return

        user_name = ""
        monthly_income = 0.0
        categories = []
        expenses = {}

        current_category = None

        for line in lines:
            if line.startswith("NAME:"):
                user_name = line.split(":", 1)[1].strip()
            elif line.startswith("INCOME:"):
                try:
                    monthly_income = float(line.split(":", 1)[1].strip())
                except ValueError:
                    monthly_income = 0.0
            elif line.startswith("CATEGORY:"):
                current_category = line.split(":", 1)[1].strip()
                categories.append(current_category)
                expenses[current_category] = []
            elif "|" in line and current_category:
                name, cost = line.split("|", 1)
                try:
                    cost = float(cost)
                    expenses[current_category].append((name, cost))
                except ValueError:
                    pass

        # Update controller state
        self.controller.user_name = user_name or "User"
        self.controller.monthly_income = monthly_income
        self.controller.categories = categories or self.controller.default_categories
        self.controller.budget_file_path = path

        # Rebuild Budget
        self.controller.budget = Budget(categories=self.controller.categories)
        for cat, items in expenses.items():
            for expense_name, cost in items:
                self.controller.budget.add_expense(cat, expense_name, cost)

        # Update UI fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.controller.user_name)

        self.income_entry.delete(0, tk.END)
        self.income_entry.insert(0, str(self.controller.monthly_income))

        self.categories_text.delete("1.0", "end")
        self.categories_text.insert("1.0", "\n".join(self.controller.categories))

        self.msg.config(text="Loaded budget from file.")

class ExpenseFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Add Expenses", font=("Arial", 16)).pack(pady=8)

        self.header = ttk.Label(self, text="")
        self.header.pack(pady=(0, 6))

        # Category dropdown
        cat_row = ttk.Frame(self)
        cat_row.pack(fill="x", padx=10, pady=(0, 8))
        ttk.Label(cat_row, text="Category:").grid(row=0, column=0, sticky="w")
        self.category_cb = ttk.Combobox(cat_row, state="readonly", values=[])
        self.category_cb.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        cat_row.columnconfigure(1, weight=1)

        # Inputs
        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=10)

        ttk.Label(frm, text="Expense name:").grid(row=0, column=0, sticky="w")
        self.expense_name = ttk.Entry(frm)
        self.expense_name.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        ttk.Label(frm, text="Cost:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.expense_cost = ttk.Entry(frm)
        self.expense_cost.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(6, 0))

        frm.columnconfigure(1, weight=1)

        # Actions
        actions = ttk.Frame(self)
        actions.pack(pady=10)
        ttk.Button(actions, text="Add Expense", command=self.add_expense).grid(row=0, column=0, padx=4)
        ttk.Button(actions, text="Done (Summary)", command=self.controller.go_to_summary).grid(row=0, column=1, padx=4)

        # Totals
        self.totals_label = ttk.Label(self, text="")
        self.totals_label.pack(pady=(6, 2))
        self.remaining_label = ttk.Label(self, text="")
        self.remaining_label.pack()

        # Status line
        self.status_line = ttk.Label(self, text="")
        self.status_line.pack(pady=(4, 0))

        # Back
        ttk.Button(self, text="Back", command=lambda: self.controller.show_frame(WelcomeFrame)).pack(pady=8)

    def refresh(self):
        # Update header and categories
        name = self.controller.user_name or "User"
        income = self.controller.monthly_income
        self.header.config(text=f"Hello, {name}! Monthly income: {format_currency(income)}")

        # Update combobox values from controller
        cats = self.controller.categories or self.controller.default_categories
        self.category_cb["values"] = cats
        if not self.category_cb.get() and cats:
            self.category_cb.set(cats[0])

        self.update_totals()

    def add_expense(self):
        if self.controller.budget is None:
            messagebox.showerror("Error", "No budget initialized. Go back and start again.")
            return

        cat = self.category_cb.get()
        name = (self.expense_name.get() or "").strip()
        cost_str = (self.expense_cost.get() or "").strip()

        if not cat or not name or not cost_str:
            messagebox.showwarning("Missing info", "Select a category and provide both name and cost.")
            return

        ok, cost = parse_float(cost_str)
        if not ok:
            messagebox.showwarning("Invalid cost", "Cost must be a valid number.")
            return

        self.controller.budget.add_expense(cat, name, cost)

        # Clear entries and update totals
        self.expense_name.delete(0, tk.END)
        self.expense_cost.delete(0, tk.END)
        self.expense_name.focus()

        self.update_totals()

    def update_totals(self):
        budget = self.controller.budget
        income = self.controller.monthly_income

        if budget is None:
            self.totals_label.config(text="No expenses yet.")
            self.remaining_label.config(text="")
            self.status_line.config(text="")
            return

        cat_totals = budget.total_by_category()
        grand = budget.total()
        remaining = calc_balance(income, grand)

        cats = self.controller.categories or self.controller.default_categories
        cat_text = ", ".join(
            f"{c}: {format_currency(cat_totals.get(c, 0.0))}" for c in cats
        )
        self.totals_label.config(text=f"Totals — {cat_text}")
        self.remaining_label.config(text=f"Remaining: {format_currency(remaining)}")
        self.status_line.config(text=financial_status_msg(remaining))
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
