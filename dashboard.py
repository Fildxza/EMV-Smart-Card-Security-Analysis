import csv
import os
import traceback
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from card_loader import CardLoader
from database import DatabaseManager
from security_analyzer import SecurityAnalyzer
from transaction_simulator import TransactionSimulator


def _startup_log(message: str) -> None:
    with open("startup_trace.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().isoformat()} | {message}\n")


THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "text": "#c9d1d9",
        "accent": "#58a6ff",
        "safe": "#2ea043",
        "warn": "#e3b341",
        "alert": "#f85149",
        "entry_bg": "#0b0f14",
        "button_bg": "#21262d",
        "button_active": "#30363d",
        "tree_heading": "#21262d",
    },
    "light": {
        "bg": "#ecf2f9",
        "panel": "#f7fbff",
        "text": "#1f2d3d",
        "accent": "#0a66c2",
        "safe": "#0d8f3f",
        "warn": "#b58105",
        "alert": "#c62828",
        "entry_bg": "#ffffff",
        "button_bg": "#dde7f3",
        "button_active": "#cbdaf0",
        "tree_heading": "#d4e2f4",
    },
}


class EMVDashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EMV Smart Card Security Analysis and Transaction Monitoring System")
        self.root.geometry("1360x860")

        self.theme_name = "dark"
        self.theme = THEMES[self.theme_name]
        self.root.configure(bg=self.theme["bg"])

        self.db = DatabaseManager()
        self.db.initialize_database()
        self.db.seed_dummy_cards()

        self.card_loader = CardLoader(self.db)
        self.simulator = TransactionSimulator()
        self.analyzer = SecurityAnalyzer(self.db)

        self.cards: List[Dict[str, Any]] = []
        self.selected_card: Optional[Dict[str, Any]] = None
        self.current_transaction: Optional[Dict[str, Any]] = None
        self.last_risk_level: Optional[str] = None

        self._build_styles()
        self._build_layout()
        self._refresh_cards()
        self._refresh_logs()
        self._refresh_graphs()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.theme["bg"])
        style.configure("Panel.TFrame", background=self.theme["panel"])
        style.configure(
            "TLabel",
            background=self.theme["panel"],
            foreground=self.theme["text"],
            font=("Consolas", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.theme["panel"],
            foreground=self.theme["accent"],
            font=("Consolas", 12, "bold"),
        )
        style.configure(
            "Risk.TLabel",
            background=self.theme["panel"],
            foreground=self.theme["text"],
            font=("Consolas", 14, "bold"),
        )
        style.configure(
            "TButton",
            background=self.theme["button_bg"],
            foreground=self.theme["text"],
            font=("Consolas", 10, "bold"),
            borderwidth=1,
            focusthickness=2,
            focuscolor=self.theme["accent"],
        )
        style.map("TButton", background=[("active", self.theme["button_active"])])

        style.configure(
            "TEntry",
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["text"],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["text"],
        )
        style.configure(
            "Treeview",
            background=self.theme["entry_bg"],
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["text"],
            font=("Consolas", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=self.theme["tree_heading"],
            foreground=self.theme["accent"],
            font=("Consolas", 9, "bold"),
        )

    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=2)

        left_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        center_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        right_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)
        bottom_panel = ttk.Frame(self.root, style="Panel.TFrame", padding=12)

        left_panel.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        center_panel.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=8, pady=8)
        bottom_panel.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=8, pady=(0, 8))

        self._build_left_panel(left_panel)
        self._build_center_panel(center_panel)
        self._build_right_panel(right_panel)
        self._build_bottom_panel(bottom_panel)

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Card Info", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Label(parent, text="Select Card:").grid(row=1, column=0, sticky="w")
        self.card_selector = ttk.Combobox(parent, state="readonly", width=44)
        self.card_selector.grid(row=2, column=0, sticky="ew", pady=(2, 10))

        self.card_info_labels: Dict[str, ttk.Label] = {}
        fields = [
            "cardholder_name",
            "bank",
            "card_type",
            "card_number",
            "expiry_date",
            "aid",
            "country",
            "currency",
        ]
        for row_idx, field in enumerate(fields, start=3):
            label = ttk.Label(parent, text=f"{field}: -")
            label.grid(row=row_idx, column=0, sticky="w", pady=2)
            self.card_info_labels[field] = label

        parent.grid_columnconfigure(0, weight=1)

    def _build_center_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Transaction Simulation", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        ttk.Label(parent, text="Amount (MYR):").grid(row=1, column=0, sticky="w")
        self.amount_var = tk.StringVar(value="100.00")
        ttk.Entry(parent, textvariable=self.amount_var, width=22).grid(row=1, column=1, sticky="w")

        self.tx_status_label = ttk.Label(parent, text="Status: -")
        self.tx_status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.tx_risk_label = ttk.Label(parent, text="Risk: -")
        self.tx_risk_label.grid(row=3, column=0, columnspan=2, sticky="w")

        self.arqc_label = ttk.Label(parent, text="ARQC: -")
        self.arqc_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.arpc_label = ttk.Label(parent, text="ARPC: -")
        self.arpc_label.grid(row=5, column=0, columnspan=2, sticky="w")

        button_frame = ttk.Frame(parent, style="Panel.TFrame")
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(15, 0))

        ttk.Button(button_frame, text="Load Card", command=self.load_selected_card).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(button_frame, text="Simulate Transaction", command=self.simulate_transaction).grid(
            row=0, column=1, padx=3, pady=3
        )
        ttk.Button(button_frame, text="Analyze", command=self.analyze_transaction).grid(row=0, column=2, padx=3, pady=3)
        ttk.Button(button_frame, text="Clear", command=self.clear_screen).grid(row=0, column=3, padx=3, pady=3)

        self.theme_button = ttk.Button(button_frame, text="Switch to Light Mode", command=self.toggle_theme)
        self.theme_button.grid(row=1, column=0, columnspan=4, padx=3, pady=(8, 3), sticky="ew")

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Security Analysis", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.risk_indicator = ttk.Label(parent, text="RISK LEVEL: -", style="Risk.TLabel")
        self.risk_indicator.grid(row=1, column=0, sticky="w", pady=(0, 8))

        ttk.Label(parent, text="Findings:").grid(row=2, column=0, sticky="w")
        self.findings_text = tk.Text(
            parent,
            height=10,
            width=44,
            bg=self.theme["entry_bg"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
            relief="flat",
            font=("Consolas", 10),
        )
        self.findings_text.grid(row=3, column=0, sticky="nsew")
        self.findings_text.configure(state="disabled")

        ttk.Label(parent, text="Graph Visualization:").grid(row=4, column=0, sticky="w", pady=(8, 4))
        self.figure = Figure(figsize=(4.4, 2.8), dpi=100)
        self.graph_canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.graph_canvas_widget = self.graph_canvas.get_tk_widget()
        self.graph_canvas_widget.grid(row=5, column=0, sticky="nsew")

        parent.grid_rowconfigure(3, weight=1)
        parent.grid_rowconfigure(5, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def _build_bottom_panel(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Logs", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(parent, text="Export Logs CSV", command=self.export_logs_csv).grid(
            row=0, column=1, sticky="e", pady=(0, 8)
        )

        columns = ("timestamp", "type", "message")
        self.log_table = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        self.log_table.heading("timestamp", text="Timestamp")
        self.log_table.heading("type", text="Type")
        self.log_table.heading("message", text="Message")
        self.log_table.column("timestamp", width=190, anchor="w")
        self.log_table.column("type", width=90, anchor="center")
        self.log_table.column("message", width=900, anchor="w")
        self.log_table.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.log_table.yview)
        self.log_table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

    def _refresh_cards(self) -> None:
        self.cards = self.card_loader.load_cards()
        values = [self.card_loader.card_display_text(card) for card in self.cards]
        self.card_selector["values"] = values

        if values:
            self.card_selector.current(0)
            self.load_selected_card()

    def _refresh_logs(self) -> None:
        for item in self.log_table.get_children():
            self.log_table.delete(item)

        for log in self.db.get_logs(limit=200):
            self.log_table.insert(
                "",
                "end",
                values=(
                    str(log["timestamp"]),
                    str(log["log_type"]),
                    str(log["message"]),
                ),
            )

    def _refresh_graphs(self) -> None:
        transactions = self.db.get_transactions(limit=30)
        chronological = list(reversed(transactions))

        self.figure.clear()
        ax_risk = self.figure.add_subplot(121)
        ax_status = self.figure.add_subplot(122)

        self.figure.patch.set_facecolor(self.theme["panel"])

        for axis in (ax_risk, ax_status):
            axis.set_facecolor(self.theme["entry_bg"])
            axis.tick_params(colors=self.theme["text"])
            axis.xaxis.label.set_color(self.theme["text"])
            axis.yaxis.label.set_color(self.theme["text"])
            axis.title.set_color(self.theme["accent"])
            for spine in axis.spines.values():
                spine.set_color(self.theme["text"])

        if chronological:
            risk_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
            risk_values = [risk_map.get(str(tx.get("risk_level", "LOW")).upper(), 1) for tx in chronological]
            x_values = list(range(1, len(risk_values) + 1))

            ax_risk.plot(x_values, risk_values, marker="o", color=self.theme["accent"], linewidth=1.8)
            ax_risk.set_title("Risk Trend")
            ax_risk.set_xlabel("Transaction #")
            ax_risk.set_yticks([1, 2, 3])
            ax_risk.set_yticklabels(["LOW", "MEDIUM", "HIGH"])
            ax_risk.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

            status_order = ["APPROVED", "FLAGGED", "DECLINED"]
            status_counts = {status: 0 for status in status_order}
            for tx in chronological:
                status = str(tx.get("status", "")).upper()
                if status in status_counts:
                    status_counts[status] += 1

            colors = [self.theme["safe"], self.theme["warn"], self.theme["alert"]]
            ax_status.bar(status_order, [status_counts[s] for s in status_order], color=colors)
            ax_status.set_title("Status Distribution")
            ax_status.set_ylabel("Count")
            ax_status.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.4)
        else:
            ax_risk.set_title("Risk Trend")
            ax_status.set_title("Status Distribution")
            ax_risk.text(0.5, 0.5, "No data", color=self.theme["text"], ha="center", va="center")
            ax_status.text(0.5, 0.5, "No data", color=self.theme["text"], ha="center", va="center")

        self.figure.tight_layout(pad=1.2)
        self.graph_canvas.draw()

    def _write_findings(self, lines: List[str]) -> None:
        self.findings_text.configure(state="normal")
        self.findings_text.delete("1.0", tk.END)
        self.findings_text.insert("1.0", "\n".join(lines))
        self.findings_text.configure(state="disabled")

    def _risk_color(self, risk: str) -> str:
        if risk == "LOW":
            return self.theme["safe"]
        if risk == "MEDIUM":
            return self.theme["warn"]
        return self.theme["alert"]

    def _apply_theme_runtime(self) -> None:
        self.theme = THEMES[self.theme_name]
        self.root.configure(bg=self.theme["bg"])
        self._build_styles()

        self.findings_text.configure(
            bg=self.theme["entry_bg"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
        )

        button_text = "Switch to Dark Mode" if self.theme_name == "light" else "Switch to Light Mode"
        self.theme_button.configure(text=button_text)

        if self.last_risk_level:
            self.risk_indicator.configure(foreground=self._risk_color(self.last_risk_level))
        else:
            self.risk_indicator.configure(foreground=self.theme["text"])

        self._refresh_graphs()

    def toggle_theme(self) -> None:
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self._apply_theme_runtime()
        self.db.save_log(f"Theme switched to {self.theme_name.upper()} mode.", "INFO")
        self._refresh_logs()

    def load_selected_card(self) -> None:
        selected = self.card_selector.get()
        card = self.card_loader.find_card_by_display(self.cards, selected)
        if not card:
            messagebox.showwarning("Card", "No card selected.")
            return

        self.selected_card = card
        for field, label in self.card_info_labels.items():
            value = card.get(field, "-")
            label.configure(text=f"{field}: {value}")

        self.db.save_log(f"Card loaded: {card['cardholder_name']} ({card['bank']})", "INFO")
        self._refresh_logs()

    def simulate_transaction(self) -> None:
        if not self.selected_card:
            messagebox.showwarning("Simulation", "Please load a card first.")
            return

        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Simulation", "Amount must be a valid number.")
            return

        self.current_transaction = self.simulator.simulate_transaction(self.selected_card, amount)

        self.tx_status_label.configure(text=f"Status: {self.current_transaction['status']}")
        self.tx_risk_label.configure(text=f"Risk: {self.current_transaction['risk_level']}")
        self.arqc_label.configure(text=f"ARQC: {self.current_transaction['arqc']}")
        self.arpc_label.configure(text=f"ARPC: {self.current_transaction['arpc']}")

        sim_notes = self.current_transaction.get("notes", [])
        self._write_findings(["Simulation output:"] + [f"- {note}" for note in sim_notes])

        self.db.save_log(
            f"Simulated tx for card_id={self.selected_card['id']}, amount={amount:.2f}, status={self.current_transaction['status']}",
            "SIM",
        )
        self._refresh_logs()

    def analyze_transaction(self) -> None:
        if not self.selected_card:
            messagebox.showwarning("Analyze", "Please load a card first.")
            return

        if not self.current_transaction:
            messagebox.showwarning("Analyze", "Simulate a transaction before analysis.")
            return

        analysis = self.analyzer.analyze(self.selected_card, self.current_transaction)
        risk_level = str(analysis["risk_level"]).upper()
        status = str(analysis["status"]).upper()
        self.last_risk_level = risk_level

        self.tx_status_label.configure(text=f"Status: {status}")
        self.tx_risk_label.configure(text=f"Risk: {risk_level}")
        self.risk_indicator.configure(
            text=f"RISK LEVEL: {risk_level}",
            foreground=self._risk_color(risk_level),
        )

        findings = analysis.get("findings", [])
        score = analysis.get("score", 0)
        display_lines = [f"Security score: {score}", "", "Findings:"] + [f"- {item}" for item in findings]
        self._write_findings(display_lines)

        amount = float(self.current_transaction["amount"])
        self.db.save_transaction(self.selected_card["id"], amount, status, risk_level)
        self.db.save_log(
            f"Analysis completed: card_id={self.selected_card['id']}, amount={amount:.2f}, status={status}, risk={risk_level}",
            "ANALYSIS",
        )
        self._refresh_logs()
        self._refresh_graphs()

    def export_logs_csv(self) -> None:
        logs = self.db.get_logs(limit=5000)
        if not logs:
            messagebox.showinfo("Export", "No logs available to export.")
            return

        default_name = f"emv_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            title="Export Logs as CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=default_name,
        )
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["id", "timestamp", "log_type", "message"])
            for log in reversed(logs):
                writer.writerow([log["id"], log["timestamp"], log["log_type"], log["message"]])

        self.db.save_log(f"Logs exported to CSV: {os.path.basename(file_path)}", "EXPORT")
        self._refresh_logs()
        messagebox.showinfo("Export", f"Logs exported successfully to\n{file_path}")

    def clear_screen(self) -> None:
        self.current_transaction = None
        self.last_risk_level = None
        self.amount_var.set("100.00")
        self.tx_status_label.configure(text="Status: -")
        self.tx_risk_label.configure(text="Risk: -")
        self.arqc_label.configure(text="ARQC: -")
        self.arpc_label.configure(text="ARPC: -")
        self.risk_indicator.configure(text="RISK LEVEL: -", foreground=self.theme["text"])
        self._write_findings(["Cleared."])

        self.db.save_log("Dashboard cleared by user.", "INFO")
        self._refresh_logs()
        self._refresh_graphs()


def main() -> None:
    try:
        _startup_log("main_start")
        root = tk.Tk()
        _startup_log("tk_root_created")
        EMVDashboard(root)
        _startup_log("dashboard_created")
        root.mainloop()
        _startup_log("mainloop_exited")
    except Exception:
        error_text = traceback.format_exc()
        _startup_log("startup_exception")
        with open("startup_error.log", "w", encoding="utf-8") as log_file:
            log_file.write(error_text)
        print(error_text)
        raise


if __name__ == "__main__":
    main()
