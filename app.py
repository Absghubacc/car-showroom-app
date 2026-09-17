import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import pymongo
from bson.objectid import ObjectId

# --- MongoDB Setup ---
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["car_showroom_db"]
    collection = db["inventory"]
except Exception as e:
    print(f"Database connection error: {e}")

# --- App Theme Configuration ---
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class CarShowroomApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("𝑪𝒂𝒓 𝑺𝒉𝒐𝒘𝒓𝒐𝒐𝒎 𝑴𝒂𝒏𝒂𝒈𝒆𝒎𝒆𝒏𝒕 | 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒅 𝑩𝒚 𝑨𝒃𝒉𝒊𝒋𝒆𝒆𝒕.𝑾")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Grid layout for Sidebar and Main Content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Αвѕнσωяσσм",font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.select_frame("dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=15)

        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="Add New Car", font=ctk.CTkFont(size=15, weight="bold"), command=lambda: self.select_frame("add"))
        self.btn_add.grid(row=2, column=0, padx=20, pady=15)

        self.btn_manage = ctk.CTkButton(self.sidebar_frame, text="Manage Inventory", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame("manage"))
        self.btn_manage.grid(row=3, column=0, padx=20, pady=15)

        # --- Main Container Frame ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Initialize View Frames with explicit keys matching button commands
        self.frames = {
            "dashboard": DashboardFrame(parent=self.main_frame, controller=self),
            "add": AddCarFrame(parent=self.main_frame, controller=self),
            "manage": ManageInventoryFrame(parent=self.main_frame, controller=self)
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.select_frame("dashboard")

    def select_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()
        if hasattr(frame, "refresh_data"):
            frame.refresh_data()

# --- 1. Dashboard Frame ---
class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        title = ctk.CTkLabel(self, text="Showroom Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        # Stats Cards Container
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.card_total = self.create_card(self.stats_frame, "Total Inventory", "0", 0)
        self.card_available = self.create_card(self.stats_frame, "Available Cars", "0", 1)
        self.card_value = self.create_card(self.stats_frame, "Portfolio Value", "$0.00", 2)

        sub_title = ctk.CTkLabel(self, text="Recent Inventory Overview", font=ctk.CTkFont(size=18, weight="bold"))
        sub_title.pack(anchor="w", pady=(30, 10))

        self.create_table()

    def create_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=0, column=col, padx=10, sticky="ew")
        
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        lbl_title.pack(pady=(15, 5))
        
        lbl_val = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"))
        lbl_val.pack(pady=(0, 15))
        return lbl_val

    def create_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("ID", "Brand", "Model", "Year", "Price", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_data(self):
        try:
            cars = list(collection.find())
            total = len(cars)
            available = len([c for c in cars if c.get("status") == "Available"])
            total_val = sum([c.get("price", 0) for c in cars])

            self.card_total.configure(text=str(total))
            self.card_available.configure(text=str(available))
            self.card_value.configure(text=f"${total_val:,.2f}")

            for row in self.tree.get_children():
                self.tree.delete(row)

            for car in cars[-5:][::-1]:
                self.tree.insert("", "end", values=(
                    str(car.get("_id"))[:8] + "...",
                    car.get("brand"),
                    car.get("model"),
                    car.get("year"),
                    f"${car.get('price', 0):,.2f}",
                    car.get("status")
                ))
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

# --- 2. Add Car Frame ---
class AddCarFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        title = ctk.CTkLabel(self, text="Add New Car to Inventory", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        form_frame.grid_columnconfigure((0, 1), weight=1)

        self.brand_input = self.create_input(form_frame, "Brand / Manufacturer", 0, 0)
        self.model_input = self.create_input(form_frame, "Model Name", 1, 0)
        self.year_input = self.create_input(form_frame, "Manufacturing Year", 2, 0)
        self.price_input = self.create_input(form_frame, "Price ($)", 3, 0)

        self.color_input = self.create_input(form_frame, "Color", 0, 1)
        
        lbl_fuel = ctk.CTkLabel(form_frame, text="Fuel Type", font=ctk.CTkFont(size=14))
        lbl_fuel.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")
        self.fuel_input = ctk.CTkComboBox(form_frame, values=["Gasoline", "Electric", "Hybrid", "Diesel"])
        self.fuel_input.grid(row=3, column=1, padx=20, pady=(0, 10), sticky="ew")

        lbl_status = ctk.CTkLabel(form_frame, text="Status", font=ctk.CTkFont(size=14))
        lbl_status.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="w")
        self.status_input = ctk.CTkComboBox(form_frame, values=["Available", "Reserved", "Sold"])
        self.status_input.grid(row=5, column=1, padx=20, pady=(0, 10), sticky="ew")

        btn_submit = ctk.CTkButton(form_frame, text="Save Car to Database", command=self.save_car, fg_color="#28a745", hover_color="#218838")
        btn_submit.grid(row=6, column=0, columnspan=2, pady=30, ipadx=20)

    def create_input(self, parent, label_text, row, col):
        lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=14))
        lbl.grid(row=row*2, column=col, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent, placeholder_text=f"Enter {label_text.lower()}")
        entry.grid(row=row*2+1, column=col, padx=20, pady=(0, 10), sticky="ew")
        return entry

    def save_car(self):
        brand = self.brand_input.get()
        model = self.model_input.get()
        year = self.year_input.get()
        price = self.price_input.get()
        color = self.color_input.get()
        fuel = self.fuel_input.get()
        status = self.status_input.get()

        if not brand or not model:
            messagebox.showerror("Error", "Brand and Model fields are required!")
            return

        try:
            car_data = {
                "brand": brand,
                "model": model,
                "year": int(year) if year else 2024,
                "price": float(price) if price else 0.0,
                "color": color,
                "fuel_type": fuel,
                "status": status
            }
            collection.insert_one(car_data)
            messagebox.showinfo("Success", f"Successfully added {brand} {model} to MongoDB!")
            
            # Clear Inputs
            self.brand_input.delete(0, 'end')
            self.model_input.delete(0, 'end')
            self.year_input.delete(0, 'end')
            self.price_input.delete(0, 'end')
            self.color_input.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

# --- 3. Manage Inventory Frame ---
class ManageInventoryFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        title = ctk.CTkLabel(self, text="Manage Inventory", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, pady=(0, 15))

        columns = ("ID", "Brand", "Model", "Year", "Price", "Fuel", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", pady=5)

        self.btn_delete = ctk.CTkButton(action_frame, text="Delete Selected Car Record", command=self.delete_car, fg_color="#dc3545", hover_color="#c82333")
        self.btn_delete.pack(side="right", padx=5, pady=5)

    def refresh_data(self):
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)

            self.cars = list(collection.find())
            for car in self.cars:
                self.tree.insert("", "end", iid=str(car.get("_id")), values=(
                    str(car.get("_id")),
                    car.get("brand"),
                    car.get("model"),
                    car.get("year"),
                    f"${car.get('price', 0):,.2f}",
                    car.get("fuel_type"),
                    car.get("status")
                ))
        except Exception as e:
            print(f"Error loading management view: {e}")

    def delete_car(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a car record from the table to delete.")
            return

        car_id = selected_item[0]
        if messagebox.askyesno("Confirmation", "Are you sure you want to permanently delete this car record?"):
            try:
                collection.delete_one({"_id": ObjectId(car_id)})
                messagebox.showinfo("Success", "Car deleted successfully!")
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = CarShowroomApp()
    app.mainloop()