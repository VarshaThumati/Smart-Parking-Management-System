import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ------------------ DB CONFIG ------------------
DB = dict(host="localhost", user="root", password="dbms", database="smart_parking")  # <-- change password if needed

def get_conn():
    return mysql.connector.connect(**DB)

# ------------------ HELPERS ------------------
def run_query(sql, params=None, fetch="all"):
    conn = cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if sql.strip().upper().startswith(("INSERT","UPDATE","DELETE","CALL","DROP","CREATE")):
            conn.commit()
        if fetch == "one":
            return cur.fetchone()
        elif fetch == "all":
            return cur.fetchall()
        else:
            return None
    except Error as e:
        raise
    finally:
        try:
            if cur: cur.close()
            if conn: conn.close()
        except:
            pass

def scalar(sql, params=None, default=None):
    row = run_query(sql, params, fetch="one")
    return (row[0] if row and row[0] is not None else default)

def query_to_tree(tree: ttk.Treeview, headers, rows):
    # reset columns
    for c in tree.get_children():
        tree.delete(c)
    tree["columns"] = headers
    tree["show"] = "headings"
    for h in headers:
        tree.heading(h, text=h)
        tree.column(h, anchor="center", stretch=True, width=max(90, int(800/len(headers))))
    for r in rows:
        tree.insert("", "end", values=r)

def vehicle_id_from_input(text):
    """Accept numeric Vehicle_ID or Plate_No; returns Vehicle_ID or None."""
    if not text:
        return None
    text = text.strip()
    if text.isdigit():
        return int(text)
    # look up by plate
    vid = scalar("SELECT Vehicle_ID FROM vehicles WHERE Plate_No = %s", (text,))
    return vid

# ------------------ APP ------------------
class SmartParkingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Parking Management — Pro")
        self.geometry("980x640")
        self.minsize(900, 580)

        # ttk styling
        style = ttk.Style(self)
        try:
            # Use a nicer theme if available
            style.theme_use("clam")
        except:
            pass
        style.configure("TButton", padding=6)
        style.configure("Card.TFrame", background="#f5f7fb")
        style.configure("CardBig.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("CardSm.TLabel", font=("Segoe UI", 10))
        style.configure("KPI.TLabel", font=("Segoe UI", 12, "bold"))

        # notebook tabs
        nb = ttk.Notebook(self)
        self.tab_dashboard = ttk.Frame(nb, padding=10)
        self.tab_parking   = ttk.Frame(nb, padding=10)
        self.tab_reports   = ttk.Frame(nb, padding=10)
        nb.add(self.tab_dashboard, text="Dashboard")
        nb.add(self.tab_parking,   text="Parking")
        nb.add(self.tab_reports,   text="Reports")
        nb.pack(fill="both", expand=True)

        self.make_dashboard()
        self.make_parking()
        self.make_reports()

        # status bar
        self.status = tk.StringVar(value="Ready")
        bar = ttk.Label(self, textvariable=self.status, anchor="w", relief="groove")
        bar.pack(fill="x", side="bottom")

        self.refresh_dashboard()
        self.refresh_reports()

    # -------- Dashboard --------
    def make_dashboard(self):
        g = ttk.Frame(self.tab_dashboard)
        g.pack(fill="both", expand=True)

        # KPI cards
        cards = ttk.Frame(g)
        cards.pack(fill="x", pady=(0, 10))

        self.kpi_slots = self.kpi_card(cards, "Available Slots", "0")
        self.kpi_active = self.kpi_card(cards, "Active Parked Vehicles", "0")
        self.kpi_today = self.kpi_card(cards, "Today's Revenue (₹)", "0.00")

        self.kpi_slots.pack(side="left", expand=True, fill="x", padx=6)
        self.kpi_active.pack(side="left", expand=True, fill="x", padx=6)
        self.kpi_today.pack(side="left", expand=True, fill="x", padx=6)

        # Recent Payments table
        box = ttk.LabelFrame(g, text="Recent Payments")
        box.pack(fill="both", expand=True)

        cols = ("Pay_ID", "Vehicle_ID", "Amount", "Date")
        self.tree_recent = ttk.Treeview(box, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree_recent.heading(c, text=c)
            self.tree_recent.column(c, anchor="center")
        self.tree_recent.pack(fill="both", expand=True, padx=6, pady=6)

        # refresh button
        ttk.Button(g, text="Refresh Dashboard", command=self.refresh_dashboard).pack(anchor="e")

    def kpi_card(self, parent, title, value_str):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(frame, text=title, style="CardSm.TLabel").pack(anchor="w")
        lbl = ttk.Label(frame, text=value_str, style="CardBig.TLabel")
        lbl.pack(anchor="w")
        return frame

    def refresh_dashboard(self):
        try:
            avail = scalar("SELECT COUNT(*) FROM available_slots", default=0)
            active = scalar("SELECT COUNT(*) FROM active_vehicles", default=0)
            today = scalar("SELECT IFNULL(SUM(Amount),0) FROM payments WHERE DATE(Date)=CURDATE()", default=0.0)

            self.kpi_slots.winfo_children()[1]["text"] = str(avail)
            self.kpi_active.winfo_children()[1]["text"] = str(active)
            self.kpi_today.winfo_children()[1]["text"] = f"{float(today):.2f}"

            rows = run_query("SELECT Pay_ID, Vehicle_ID, Amount, Date FROM payments ORDER BY Pay_ID DESC LIMIT 10")
            query_to_tree(self.tree_recent, ("Pay_ID","Vehicle_ID","Amount","Date"), rows)
            self.status.set("Dashboard refreshed")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            self.status.set("Error refreshing dashboard")

    # -------- Parking --------
    def make_parking(self):
        grid = ttk.Frame(self.tab_parking)
        grid.pack(fill="both", expand=True)

        # Enter group
        enter = ttk.LabelFrame(grid, text="Enter (Park) Vehicle")
        enter.pack(fill="x", pady=6)

        ttk.Label(enter, text="Vehicle (ID or Plate):").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.ent_enter_vehicle = ttk.Entry(enter, width=24)
        self.ent_enter_vehicle.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        self.var_auto = tk.BooleanVar(value=True)
        chk = ttk.Checkbutton(enter, text="Auto-allocate first available slot", variable=self.var_auto, command=self.toggle_slot_entry)
        chk.grid(row=0, column=2, padx=6, pady=6, sticky="w")

        ttk.Label(enter, text="Slot ID (if not auto):").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        self.ent_slot = ttk.Entry(enter, width=12, state="disabled")
        self.ent_slot.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ttk.Button(enter, text="Park Vehicle", command=self.handle_enter).grid(row=1, column=2, padx=6, pady=6)

        # Exit group
        exitf = ttk.LabelFrame(grid, text="Exit Vehicle (sets Exit_Time, calculates fee)")
        exitf.pack(fill="x", pady=6)

        ttk.Label(exitf, text="Vehicle (ID or Plate):").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.ent_exit_vehicle = ttk.Entry(exitf, width=24)
        self.ent_exit_vehicle.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Button(exitf, text="Exit & Calculate Fee", command=self.handle_exit).grid(row=0, column=2, padx=6, pady=6)

        # Quick views under Parking
        views = ttk.Frame(grid)
        views.pack(fill="both", expand=True, pady=(8,0))

        # Active vehicles
        left = ttk.LabelFrame(views, text="Active Parked Vehicles")
        left.pack(side="left", fill="both", expand=True, padx=(0,6))
        self.tree_active = ttk.Treeview(left, columns=("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"), show="headings")
        for c in ("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"):
            self.tree_active.heading(c, text=c)
            self.tree_active.column(c, anchor="center")
        self.tree_active.pack(fill="both", expand=True, padx=6, pady=6)

        # Available slots
        right = ttk.LabelFrame(views, text="Available Slots")
        right.pack(side="left", fill="both", expand=True, padx=(6,0))
        self.tree_slots = ttk.Treeview(right, columns=("Slot_ID","Level"), show="headings")
        for c in ("Slot_ID","Level"):
            self.tree_slots.heading(c, text=c)
            self.tree_slots.column(c, anchor="center")
        self.tree_slots.pack(fill="both", expand=True, padx=6, pady=6)

        btns = ttk.Frame(grid)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Refresh Lists", command=self.refresh_parking_lists).pack(side="right")

    def toggle_slot_entry(self):
        if self.var_auto.get():
            self.ent_slot.configure(state="disabled")
        else:
            self.ent_slot.configure(state="normal")

    def refresh_parking_lists(self):
        try:
            rows_a = run_query("SELECT Vehicle_ID, Owner_Name, Plate_No, Slot_ID, Entry_Time FROM active_vehicles ORDER BY Entry_Time DESC")
            query_to_tree(self.tree_active, ("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"), rows_a)
            rows_s = run_query("SELECT Slot_ID, Level FROM available_slots ORDER BY Slot_ID")
            query_to_tree(self.tree_slots, ("Slot_ID","Level"), rows_s)
            self.status.set("Parking lists refreshed")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            self.status.set("Error refreshing parking lists")

    def handle_enter(self):
        text = self.ent_enter_vehicle.get().strip()
        vid = vehicle_id_from_input(text)
        if not vid:
            messagebox.showwarning("Input", "Enter a valid Vehicle ID or Plate No that exists in 'vehicles'.")
            return

        try:
            if self.var_auto.get():
                # pick first available slot
                slot_id = scalar("SELECT MIN(Slot_ID) FROM parking_slots WHERE Status='Available'")
                if slot_id is None:
                    messagebox.showinfo("No Slots", "No available slots right now.")
                    return
            else:
                s = self.ent_slot.get().strip()
                if not s.isdigit():
                    messagebox.showwarning("Input", "Enter a numeric Slot ID or enable Auto-allocate.")
                    return
                slot_id = int(s)

            # create entry (trigger makes slot Occupied)
            run_query("INSERT INTO entry_exit (Vehicle_ID, Slot_ID) VALUES (%s,%s)", (vid, slot_id), fetch=None)
            self.status.set(f"Vehicle {vid} parked in Slot {slot_id} at {datetime.now().strftime('%H:%M:%S')}")
            self.refresh_dashboard()
            self.refresh_parking_lists()
            messagebox.showinfo("Success", f"Parked: Vehicle {vid} → Slot {slot_id}")
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def handle_exit(self):
        text = self.ent_exit_vehicle.get().strip()
        vid = vehicle_id_from_input(text)
        if not vid:
            messagebox.showwarning("Input", "Enter a valid Vehicle ID or Plate No.")
            return

        try:
            # close the latest open entry for this vehicle
            sql = """
                UPDATE entry_exit
                SET Exit_Time = NOW()
                WHERE Entry_ID = (
                  SELECT t.Entry_ID FROM (
                    SELECT Entry_ID
                    FROM entry_exit
                    WHERE Vehicle_ID = %s AND Exit_Time IS NULL
                    ORDER BY Entry_ID DESC
                    LIMIT 1
                  ) t
                )
            """
            run_query(sql, (vid,), fetch=None)

            # call procedure for fee
            conn = get_conn()
            cur = conn.cursor()
            try:
                cur.callproc("Calculate_Fee", [vid])
                fee_rows = []
                for res in cur.stored_results():
                    fee_rows.extend(res.fetchall())
            finally:
                conn.commit()
                cur.close(); conn.close()

            msg = "Vehicle exited."
            if fee_rows:
                hours, amount = fee_rows[0]
                msg += f" Hours: {hours}, Amount: ₹{float(amount):.2f}"
            self.status.set(msg)
            self.refresh_dashboard()
            self.refresh_parking_lists()
            messagebox.showinfo("Success", msg)
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # -------- Reports --------
    def make_reports(self):
        wrap = ttk.Frame(self.tab_reports)
        wrap.pack(fill="both", expand=True)

        # top controls
        controls = ttk.Frame(wrap)
        controls.pack(fill="x")
        ttk.Button(controls, text="Refresh Reports", command=self.refresh_reports).pack(side="right", padx=6, pady=6)

        # three tables
        top = ttk.Frame(wrap)
        top.pack(fill="both", expand=True)

        frame1 = ttk.LabelFrame(top, text="Available Slots")
        frame2 = ttk.LabelFrame(top, text="Active Vehicles")
        frame3 = ttk.LabelFrame(top, text="Payments (latest 25)")
        frame1.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        frame2.pack(side="left", fill="both", expand=True, padx=4, pady=6)
        frame3.pack(side="left", fill="both", expand=True, padx=4, pady=6)

        self.r_slots = ttk.Treeview(frame1, columns=("Slot_ID","Level"), show="headings")
        for c in ("Slot_ID","Level"):
            self.r_slots.heading(c, text=c); self.r_slots.column(c, anchor="center")
        self.r_slots.pack(fill="both", expand=True, padx=6, pady=6)

        self.r_active = ttk.Treeview(frame2, columns=("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"), show="headings")
        for c in ("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"):
            self.r_active.heading(c, text=c); self.r_active.column(c, anchor="center")
        self.r_active.pack(fill="both", expand=True, padx=6, pady=6)

        self.r_payments = ttk.Treeview(frame3, columns=("Pay_ID","Vehicle_ID","Amount","Date"), show="headings")
        for c in ("Pay_ID","Vehicle_ID","Amount","Date"):
            self.r_payments.heading(c, text=c); self.r_payments.column(c, anchor="center")
        self.r_payments.pack(fill="both", expand=True, padx=6, pady=6)

    def refresh_reports(self):
        try:
            query_to_tree(self.r_slots, ("Slot_ID","Level"),
                          run_query("SELECT Slot_ID, Level FROM available_slots ORDER BY Slot_ID"))
            query_to_tree(self.r_active, ("Vehicle_ID","Owner_Name","Plate_No","Slot_ID","Entry_Time"),
                          run_query("SELECT Vehicle_ID, Owner_Name, Plate_No, Slot_ID, Entry_Time FROM active_vehicles ORDER BY Entry_Time DESC"))
            query_to_tree(self.r_payments, ("Pay_ID","Vehicle_ID","Amount","Date"),
                          run_query("SELECT Pay_ID, Vehicle_ID, Amount, Date FROM payments ORDER BY Pay_ID DESC LIMIT 25"))
            self.status.set("Reports refreshed")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            self.status.set("Error refreshing reports")

if __name__ == "__main__":
    app = SmartParkingApp()
    app.mainloop()