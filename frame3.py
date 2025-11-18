# -------- Frame 3: Summary (table + warning + SAVE BUDGET) --------
class SummaryFrame(ttk.Frame):
    def __init__(self, parent, controller: App):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Spending Summary", font=("Arial", 16)).pack(pady=8)

        self.topline = ttk.Label(self, text="")
        self.topline.pack()

        self.warn = ttk.Label(self, text="", foreground="red")
        self.warn.pack(pady=(2, 8))

        # Table
        self.tree = ttk.Treeview(self, columns=("category", "total"), show="headings", height=6)
        self.tree.heading("category", text="Category")
        self.tree.heading("total", text="Total Spent")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("total", width=140, anchor="e")
        self.tree.pack(fill="x", padx=10, pady=(0, 8))

        # Nav + save
        nav = ttk.Frame(self)
        nav.pack(pady=6)
        ttk.Button(nav, text="Back to Expenses", command=lambda: controller.show_frame(ExpenseFrame)).grid(row=0, column=0, padx=4)
        ttk.Button(nav, text="Back to Start", command=lambda: controller.show_frame(WelcomeFrame)).grid(row=0, column=1, padx=4)
        ttk.Button(nav, text="Save Budget to File", command=self.save_budget).grid(row=0, column=2, padx=4)

    def refresh(self):
        budget = self.controller.budget
        income = self.controller.monthly_income

        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        if budget is None:
            self.topline.config(text="No data yet. Add expenses first.")
            self.warn.config(text="")
            return

        # Populate per-category totals
        cats = self.controller.categories or self.controller.default_categories
        cat_totals = budget.total_by_category()
        for cat in cats:
            total = cat_totals.get(cat, 0.0)
            self.tree.insert("", "end", values=(cat, format_currency(total)))

        # Topline numbers + warning
        grand = budget.total()
        remaining = calc_balance(income, grand)
        self.topline.config(
            text=f"Income: {format_currency(income)}    "
                 f"Total Spent: {format_currency(grand)}    "
                 f"Remaining: {format_currency(remaining)}"
        )

        self.warn.config(text="" if remaining >= 0 else "WARNING: You are overspending.")
    def save_budget(self):
        controller = self.controller
        budget = controller.budget

        if budget is None:
            messagebox.showwarning("No data", "There is no budget data to save yet.")
            return

        data_lines = []
        data_lines.append(f"NAME: {controller.user_name}")
        data_lines.append(f"INCOME: {controller.monthly_income}")
        data_lines.append("")  # blank line

        for category in controller.categories:
            data_lines.append(f"CATEGORY: {category}")
            for name, cost in budget.data.get(category, []):
                data_lines.append(f"{name}|{cost}")
            data_lines.append("")  # blank line after each category

        path = controller.budget_file_path

        # If no file is linked, prompt user to choose a location
        if not path:
            path = filedialog.asksaveasfilename(
                title="Save Budget File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if not path:
                return
            controller.budget_file_path = path

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(data_lines))
        except OSError as e:
            messagebox.showerror("Error", f"Could not write budget file:\n{e}")
            return

        messagebox.showinfo("Saved", f"Budget saved to:\n{path}")
