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