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


if __name__ == "__main__":
    app = App()
    app.mainloop()
