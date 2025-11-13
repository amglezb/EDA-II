import os
import json
from datetime import datetime

class User:
    def __init__(self, user_id, name, password):
        self.id = user_id
        self.name = name
        self.password = password

class Transaction:
    def __init__(self, trans_id, user_id, amount, category, date, is_deductible, is_income, description):
        self.id = trans_id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.date = date
        self.is_deductible = is_deductible
        self.is_income = is_income
        self.description = description

class Data:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class BTreeNode:
    def __init__(self, t, leaf):
        self.t = t
        self.keys = [None] * (2 * t - 1)
        self.C = [None] * (2 * t)
        self.n = 0
        self.leaf = leaf

    def insertNonFull(self, data):
        i = self.n - 1
        if self.leaf:
            while i >= 0 and self.keys[i].key > data.key:
                self.keys[i + 1] = self.keys[i]
                i -= 1
            self.keys[i + 1] = data
            self.n += 1
        else:
            while i >= 0 and self.keys[i].key > data.key:
                i -= 1
            if self.C[i + 1].n == 2 * self.t - 1:
                self.splitChild(i + 1, self.C[i + 1])
                if self.keys[i + 1].key < data.key:
                    i += 1
            self.C[i + 1].insertNonFull(data)

    def splitChild(self, i, y):
        z = BTreeNode(y.t, y.leaf)
        z.n = self.t - 1
        for j in range(self.t - 1):
            z.keys[j] = y.keys[j + self.t]
        if not y.leaf:
            for j in range(self.t):
                z.C[j] = y.C[j + self.t]
        y.n = self.t - 1
        for j in range(self.n, i, -1):
            self.C[j + 1] = self.C[j]
        self.C[i + 1] = z
        for j in range(self.n - 1, i - 1, -1):
            self.keys[j + 1] = self.keys[j]
        self.keys[i] = y.keys[self.t - 1]
        self.n += 1

    def traverse(self, output_list):
        for i in range(self.n):
            if not self.leaf:
                self.C[i].traverse(output_list)
            output_list.append(self.keys[i])
        if not self.leaf:
            self.C[self.n].traverse(output_list)

    def search(self, k):
        i = 0
        while i < self.n and k > self.keys[i].key:
            i += 1
        if i < self.n and k == self.keys[i].key:
            return self.keys[i]
        if self.leaf:
            return None
        return self.C[i].search(k)

    def range_search(self, min_key, max_key, result_list):
        """
        Busca todas las claves dentro del rango [min_key, max_key].
        Agrega los resultados a result_list.
        """
        i = 0

        # Avanza hasta encontrar la primera clave >= min_key
        while i < self.n and self.keys[i].key < min_key:
            if not self.leaf:
                self.C[i].range_search(min_key, max_key, result_list)
            i += 1

        # Desde aquí, procesa todas las claves dentro del rango
        while i < self.n and self.keys[i].key <= max_key:
            if not self.leaf:
                self.C[i].range_search(min_key, max_key, result_list)
            result_list.append(self.keys[i])
            i += 1

        # Si aún hay hijos pendientes, procesar el siguiente
        if not self.leaf and i < len(self.C) and self.C[i]:
            self.C[i].range_search(min_key, max_key, result_list)

    def exact_search(self, key, result_list):
        """
        Busca todas las claves iguales a 'key' en este subárbol.
        Agrega los resultados a result_list.
        """
        i = 0
        while i < self.n and key > self.keys[i].key:
            i += 1

        # Recorre el subárbol izquierdo si corresponde
        if not self.leaf:
            self.C[i].exact_search(key, result_list)

        # Si la clave coincide, agregarla
        if i < self.n and self.keys[i] and self.keys[i].key == key:
            result_list.append(self.keys[i])

        # Si hay más ocurrencias a la derecha, seguir buscando
        if not self.leaf and i + 1 < len(self.C) and self.C[i + 1]:
            self.C[i + 1].exact_search(key, result_list)

class BTree:
    def __init__(self, t):
        self.root = None
        self.t = t

    def traverse(self):
        output_list = []
        if self.root != None:
            self.root.traverse(output_list)
        return output_list

    def search(self, k):
        return None if self.root == None else self.root.search(k)

    def insert(self, data):
        if self.root == None:
            self.root = BTreeNode(self.t, True)
            self.root.keys[0] = data
            self.root.n = 1
        else:
            if self.root.n == 2 * self.t - 1:
                s = BTreeNode(self.t, False)
                s.C[0] = self.root
                s.splitChild(0, self.root)
                i = 0
                if s.keys[0].key < data.key:
                    i += 1
                s.C[i].insertNonFull(data)
                self.root = s
            else:
                self.root.insertNonFull(data)

    def range_search(self, min_key, max_key):
        """Devuelve una lista de Data con claves dentro del rango."""
        result_list = []
        if self.root:
            self.root.range_search(min_key, max_key, result_list)
        return result_list

    def exact_search(self, key):
        """Devuelve una lista de Data con claves iguales a key."""
        result_list = []
        if self.root:
            self.root.exact_search(key, result_list)
        return result_list
    
class FileController:
    def __init__(self):
        self.users_file = "users.json"
        self.transactions_file = "transactions.json"
        self.transaction_tree = BTree(2)
        self.users_tree = BTree(2)

        # Árboles secundarios para transacciones del usuario activo
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.is_deductible_tree = BTree(2)
        self.is_income_tree = BTree(2)

        self._initialize_files()
        self._load_users_to_btree()
        self._load_transactions_to_btree()

    def _load_users_to_btree(self):
        """Carga los usuarios desde users.json al árbol B."""
        users = self.load_json(self.users_file)
        for u in users:
            user_obj = User(u["id"], u["name"], u["password"])
            self.users_tree.insert(Data(user_obj.id, user_obj))

    def _initialize_files(self):
        import json
        for file in [self.users_file, self.transactions_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f)
            else:
                try:
                    with open(file, "r") as f:
                        json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ {file} was corrupted. Reinitializing...")
                    with open(file, "w") as f:
                        json.dump([], f)

    def load_json(self, file):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"⚠️ File {file} was empty or invalid. Resetting...")
            with open(file, "w") as f:
                json.dump([], f)
            return []

    def save_json(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    def verify_user(self, user_id, password):
        node = self.users_tree.search(user_id)
        if node and node.value.password == password:
            return node.value
        return None

    def get_next_id(self):
        transactions = self.load_json(self.transactions_file)
        if not transactions:
            return 1
        return max(t["id"] for t in transactions) + 1

    # ------------------- Transaction Handling -------------------
    def save_transaction(self, transaction):
        transactions = self.load_json(self.transactions_file)
        transactions.append(transaction.__dict__)
        self.save_json(self.transactions_file, transactions)
        self.transaction_tree.insert(Data(transaction.id, transaction))

        # Insertar también en los árboles secundarios si pertenece al usuario activo
        self.amount_tree.insert(Data(transaction.amount, transaction))
        self.category_tree.insert(Data(transaction.category, transaction))
        self.date_tree.insert(Data(transaction.date, transaction))
        self.is_deductible_tree.insert(Data(transaction.is_deductible, transaction))
        self.is_income_tree.insert(Data(transaction.is_income, transaction))

    def _load_transactions_to_btree(self):
        """Loads existing transactions from file into the B-Tree."""
        transactions = self.load_json(self.transactions_file)
        for t in transactions:
            obj = Transaction(
                t["id"], t["user_id"], t["amount"], t["category"],
                t["date"], t["is_deductible"], t["is_income"], t["description"]
            )
            self.transaction_tree.insert(Data(obj.id, obj))

    def load_user_secondary_trees(self, user_id):
        """Carga árboles secundarios (amount, category, etc.) solo para el usuario activo."""
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.is_deductible_tree = BTree(2)
        self.is_income_tree = BTree(2)

        transactions = self.load_json(self.transactions_file)
        for t in transactions:
            if t["user_id"] == user_id:
                obj = Transaction(
                    t["id"], t["user_id"], t["amount"], t["category"],
                    t["date"], t["is_deductible"], t["is_income"], t["description"]
                )
                self.amount_tree.insert(Data(obj.amount, obj))
                self.category_tree.insert(Data(obj.category, obj))
                self.date_tree.insert(Data(obj.date, obj))
                self.is_deductible_tree.insert(Data(obj.is_deductible, obj))
                self.is_income_tree.insert(Data(obj.is_income, obj))

    def find_transaction(self, trans_id):
        node = self.transaction_tree.search(trans_id)
        return node.value if node else None

    def update_transaction(self, trans_id, field, new_value):
        transactions = self.load_json(self.transactions_file)
        updated = False
        for t in transactions:
            if t["id"] == trans_id:
                t[field] = new_value
                updated = True
                break

        if updated:
            self.save_json(self.transactions_file, transactions)
            trans = self.find_transaction(trans_id)
            if trans:
                setattr(trans, field, new_value)

                # 🔁 Si el campo afecta índices, recargar árboles secundarios
                if field in ["amount", "category", "date", "is_deductible", "is_income"]:
                    if hasattr(self, "current_user_id"):
                        self.load_user_secondary_trees(self.current_user_id)

        return updated
    
    def delete_transaction(self, trans_id):
        transactions = self.load_json(self.transactions_file)
        new_data = [t for t in transactions if t["id"] != trans_id]
        if len(new_data) == len(transactions):
            return False
        self.save_json(self.transactions_file, new_data)
        self.transaction_tree = BTree(3)
        self._load_transactions_to_btree()

        # 🔁 Si hay un usuario activo, recargar sus árboles secundarios
        if hasattr(self, "current_user_id"):
            self.load_user_secondary_trees(self.current_user_id)
        return True
    
    # ------------------- Merge Sort -------------------
    def merge_sort(self, items, key="amount"):
        if len(items) <= 1:
            return items
        mid = len(items) // 2
        left = self.merge_sort(items[:mid], key)
        right = self.merge_sort(items[mid:], key)
        return self.merge(left, right, key)

    def merge(self, left, right, key):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if getattr(left[i], key) <= getattr(right[j], key):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result += left[i:]
        result += right[j:]
        return result
    
    def buscar_isr_en_tabla(self, ingreso):
        tabla = [(0.01, 746.04, 0.00, 1.92), (746.05, 6332.05, 14.32, 6.40), (6332.06, 11128.01, 371.83, 10.88), (11128.02, 12935.82, 893.63, 16.00), (12935.83, 15487.71, 1182.88, 17.92), (15487.72, 31236.49, 1640.18, 21.36), (31236.50, 49233.00, 5004.12, 23.52), (49233.01, 93993.90, 9236.89, 30.00), (93993.91, 125325.20, 22665.17, 32.00), (125325.21, 375975.61, 32691.18, 34.00), (375975.62, float("inf"), 117912.32, 35.00)]
        izquierda, derecha = 0, len(tabla) - 1

        while izquierda <= derecha:
            mid = (izquierda + derecha) // 2
            lim_inf, lim_sup, cuota_fija, porcentaje = tabla[mid]
            if lim_inf <= ingreso <= lim_sup:
                return tabla[mid]
            elif ingreso < lim_inf:
                derecha = mid - 1
            else:
                izquierda = mid + 1
        return tabla[-1]  # en caso de superar el último rango

class System:
    def __init__(self): # sip
        self.files = FileController()
        self.current_user = None

    def login(self, user_id=None, password=None):
        try:
            if user_id is None:
                user_id = int(input("Enter your ID: "))
            if password is None:
                password = input("Enter your Password: ")
        except ValueError:
            print("❌ Invalid ID format. Please enter a numeric value.\n")
            return False

        user = self.files.verify_user(user_id, password)
        print()
        if user:
            self.current_user = user
            self.files.load_user_secondary_trees(user.id)
            print(f"\t✅ Welcome {user.name}\n")
            return True
        else:
            print("\t❌ Invalid user ID or password.\n")
            return False

    def logout(self):
        if self.current_user:
            print(f"\t----- Logged out for {self.current_user.name}\n\n")
            self.current_user = None
            # Reset secondary trees
            self.files.amount_tree = BTree(2)
            self.files.category_tree = BTree(2)
            self.files.date_tree = BTree(2)
            self.files.is_deductible_tree = BTree(2)
            self.files.is_income_tree = BTree(2)

    def show_menu(self): # sip
        print("\n\t\t\t=============== SYSTEM MENU ===============")
        print("\t\t\t1. Register New Transaction")
        print("\t\t\t2. View Transaction Data")
        print("\t\t\t3. Modify Transaction Data")
        print("\t\t\t4. Delete Transaction")
        print("\t\t\t5. Generate Transaction Report")
        print("\t\t\t6. Calculate Taxes (ISR)")
        print("\t\t\t7. Logout")
        try: option = int(input("Select an option: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            option = 0
        return option

    def register_transaction(self):
        if not self.current_user:
            print("⚠️ You must log in first.")
            return

        try:
            amount = float(input("Amount: "))
            if amount <= 0:
                print("❌ Amount must be greater than 0.")
                return
        except ValueError:
            print("❌ Invalid input. Please enter a numeric amount.")
            return

        try:
            is_deductible = int(input("Is deductible? (0 -> No, 1 -> Yes): "))
            if is_deductible not in [0, 1]:
                print("❌ Invalid option. Please enter 0 or 1.")
                return

            is_income = int(input("Is income? (0 -> Expense, 1 -> Income): "))
            if is_income not in [0, 1]:
                print("❌ Invalid option. Please enter 0 or 1.")
                return
        except ValueError:
            print("❌ Invalid input. Please enter numbers only.")
            return

        categories = ["Salary", "Donation", "Investment", "Housing", "Food", "Health",
                      "Transport", "Education", "Debts", "Other"]
        print("\nAvailable Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        try:
            cat_choice = int(input("Select category: "))
            if cat_choice < 1 or cat_choice > len(categories):
                print("❌ Invalid category number.")
                return
            category = categories[cat_choice - 1]
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return

        description = input("Description: ").strip()
        if not description:
            print("⚠️ Empty description. Transaction will be saved without description.")

        trans_id = self.files.get_next_id()
        date = datetime.now().strftime("%Y-%m-%d")

        new_trans = Transaction(trans_id, self.current_user.id, amount, category, date,
                                is_deductible, is_income, description)

        self.files.save_transaction(new_trans)
        print(f"✅ Transaction #{trans_id} registered successfully.")
    
    def view_transaction(self): # sip
        trans_id = int(input("Enter transaction ID: "))
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("Transaction not found or not owned by this user.")
            return
        print(f"\n--- Transaction #{trans.id} ---\nCategory: {trans.category}\nAmount: ${trans.amount}\nDate: {trans.date}\nDeductible: {'Yes' if trans.is_deductible else 'No'}\nType: {'Income' if trans.is_income else 'Expense'}\nDescription: {trans.description}")

    def modify_transaction(self): # sip
        trans_id = int(input("Enter transaction ID: "))
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("❌ Transaction not found or not owned by this user.")
            return

        while True:
            print("\nSelect field to modify:\n1. Amount\n2. Is Deductible\n3. Is Income\n4. Category\n5. Description\n6. Exit")
            op = int(input("Option: "))
            if op == 6: break
            field_map = {1: "amount", 2: "is_deductible", 3: "is_income", 4: "category", 5: "description"}
            field = field_map.get(op)
            if not field:
                print("Invalid option.")
                continue

            new_value = input(f"Enter new value for {field}: ")
            if field in ["amount"]: new_value = float(new_value)
            elif field in ["is_deductible", "is_income"]: new_value = int(new_value)
            elif field == "category":
                categories = ["Salary", "Donation", "Investment", "Housing", "Food", "Health", "Transport", "Education", "Debts", "Other"]
                for i, cat in enumerate(categories, 1):
                    print(f"{i}. {cat}")
                new_value = categories[int(new_value) - 1]

            self.files.update_transaction(trans_id, field, new_value)
            print("Field updated successfully.")

    def delete_transaction(self): # sip
        trans_id = int(input("Enter transaction ID to delete: "))
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("Transaction not found or not owned by this user.")
            return
        
        if self.files.delete_transaction(trans_id): print(f"Transaction #{trans_id} deleted successfully.")
        else: print("Transaction not found.")

    def generate_report(self): # sip
        if not self.current_user:
            print("⚠️ You must log in first to generate a report.")
            return

        # Verificar que existan transacciones
        all_trans = self.files.transaction_tree.traverse()
        if not all_trans:
            print("⚠️ There are no transactions available to report.")
            return

        print("\n===== GENERATE ADVANCED REPORT =====")
        print("You can filter transactions by multiple criteria.\n")

        all_results = None                 # conjunto acumulado de IDs
        applied_filters = []               # lista de sets de resultados individuales
        combined_title = []                # descripciones de filtros aplicados

        while True:
            print("\nSelect a filter criterion:")
            print("1. Amount range")
            print("2. Category")
            print("3. Date range")
            print("4. Is Deductible")
            print("5. Is Income")
            print("7. Undo last filter")
            print("6. Done (generate report)")

            try:
                op = int(input("Option: "))
            except ValueError:
                print("Invalid input.")
                continue

            if op == 6:
                break

            # === Undo last filter ===
            if op == 7:
                if not applied_filters:
                    print("⚠️ No filters to undo.")
                    continue
                removed_filter = combined_title.pop()
                applied_filters.pop()
                if applied_filters:
                    all_results = set.intersection(*applied_filters)
                else:
                    all_results = None
                print(f"↩️  Filter undone: {removed_filter}")
                if all_results:
                    print(f"→ Remaining results: {len(all_results)} transactions")
                else:
                    print("No filters active now.")
                continue

            current_set = set()
            title_part = ""

            # === Amount range ===
            if op == 1:
                try:
                    min_a = float(input("Minimum amount: "))
                    max_a = float(input("Maximum amount: "))
                    if max_a < min_a:
                        print("❌ Invalid range: maximum amount must be greater than or equal to minimum amount.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
                    continue

                found = [d.value for d in self.files.amount_tree.range_search(min_a, max_a)]
                current_set = {t.id for t in found}
                title_part = f"Amount ${min_a}–${max_a}"

            # === Category ===
            elif op == 2:
                all_cats = sorted(list({d.key for d in self.files.category_tree.traverse()}))
                if not all_cats:
                    print("No categories found for this user.")
                    continue
                print("\nAvailable categories:")
                for i, cat in enumerate(all_cats, start=1):
                    print(f"{i}. {cat}")
                try:
                    selected = int(input("Select a category number: "))
                    if selected < 1 or selected > len(all_cats):
                        print("Invalid selection.")
                        continue
                    cat = all_cats[selected - 1]
                except ValueError:
                    print("Invalid input.")
                    continue
                found = [d.value for d in self.files.category_tree.exact_search(cat)]
                current_set = {t.id for t in found}
                title_part = f"Category '{cat}'"

            # === Date range ===
            elif op == 3:
                start = input("From (YYYY-MM-DD): ")
                end = input("To (YYYY-MM-DD): ")
                try:
                    from datetime import datetime
                    start_dt = datetime.strptime(start, "%Y-%m-%d")
                    end_dt = datetime.strptime(end, "%Y-%m-%d")
                    if end_dt < start_dt:
                        print("❌ Invalid range: end date must be the same or after start date.")
                        continue
                except ValueError:
                    print("❌ Invalid date format. Please use YYYY-MM-DD.")
                    continue

                found = [d.value for d in self.files.date_tree.range_search(start, end)]
                current_set = {t.id for t in found}
                title_part = f"Dates {start}–{end}"

            # === Deductible ===
            elif op == 4:
                print("1. Only Deductible\n2. Only Not Deductible\n3. Both")
                try:
                    sel_d = int(input("Select option: "))
                except ValueError:
                    print("Invalid input.")
                    continue

                if sel_d == 1:
                    found = [d.value for d in self.files.is_deductible_tree.exact_search(1)]
                    current_set = {t.id for t in found}
                    title_part = "Deductible only"
                elif sel_d == 2:
                    found = [d.value for d in self.files.is_deductible_tree.exact_search(0)]
                    current_set = {t.id for t in found}
                    title_part = "Not deductible only"
                elif sel_d == 3:
                    found_yes = [d.value for d in self.files.is_deductible_tree.exact_search(1)]
                    found_no = [d.value for d in self.files.is_deductible_tree.exact_search(0)]
                    all_found = found_yes + found_no
                    current_set = {t.id for t in all_found}
                    title_part = "Both deductible and not deductible"
                else:
                    print("Invalid selection.")
                    continue

            # === Income / Expense ===
            elif op == 5:
                print("1. Income\n2. Expense\n3. Both")
                try:
                    sel = int(input("Select type: "))
                    if sel not in [1, 2, 3]:
                        print("Invalid option.")
                        continue
                except ValueError:
                    print("Invalid input.")
                    continue
                if sel == 3:
                    found_income = [d.value for d in self.files.is_income_tree.exact_search(1)]
                    found_expense = [d.value for d in self.files.is_income_tree.exact_search(0)]
                    all_found = found_income + found_expense
                    current_set = {t.id for t in all_found}
                    title_part = "Both income and expense"
                else:
                    found = [d.value for d in self.files.is_income_tree.exact_search(1 if sel == 1 else 0)]
                    current_set = {t.id for t in found}
                    title_part = "Income" if sel == 1 else "Expense"

            else:
                print("Invalid option.")
                continue

            # === Apply filter ===
            applied_filters.append(current_set)
            combined_title.append(title_part)

            if applied_filters:
                all_results = set.intersection(*applied_filters)
            else:
                all_results = current_set

            print(f"✅ Filter applied: {title_part}")
            print(f"→ Remaining results: {len(all_results)} transactions")

            another = input("Add another filter? (y/n): ").strip().lower()
            if another != "y":
                break

        # === No results ===
        if not all_results:
            print("\nNo transactions found with the selected filters.")
            return

        # === Get matching transactions ===
        results = [d.value for d in self.files.transaction_tree.traverse()
                   if d.value.id in all_results]
        results = self.files.merge_sort(results, "amount")

        # === Show results ===
        print("\n\n=== Filtered Transactions ===")
        for t in results:
            print(f"\nID: {t.id} | Category: {t.category} | Amount: ${t.amount} | Date: {t.date}")
            print(f"Deductible: {'Yes' if t.is_deductible else 'No'} | Type: {'Income' if t.is_income else 'Expense'}")
            print(f"Description: {t.description}")
            print("-" * 60)

        # === Ask for export ===
        choice = input("\nGenerate a text report file? (y/n): ").strip().lower()
        if choice != "y":
            print("Report generation canceled.")
            return

        # === Generate file ===
        existing_reports = [f for f in os.listdir() if f.startswith("transaction report #")]
        report_num = len(existing_reports) + 1
        filename = f"transaction report #{report_num}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Advanced Report\n")
            f.write("Filters: " + ", ".join(combined_title) + "\n")
            f.write(f"User: {self.current_user.name}\n\n")
            for t in results:
                f.write(f"ID: {t.id}\nCategory: {t.category}\nAmount: ${t.amount}\nDate: {t.date}\n"
                        f"Description: {t.description}\nDeductible: {'Yes' if t.is_deductible else 'No'}\n"
                        f"Type: {'Income' if t.is_income else 'Expense'}\n")
                f.write("-" * 50 + "\n")

        print(f"\n✅ Report file generated successfully: {filename}")

    def calculate_taxes(self):
        if not self.current_user:
            print("⚠️ You must log in first.")
            return

        start = input("Enter start date (YYYY-MM-DD): ")
        end = input("Enter end date (YYYY-MM-DD): ")
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            if end_dt < start_dt:
                print("❌ Invalid range: end date must be after start date.")
                return
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            return

        # Buscar transacciones del usuario dentro del rango
        all_trans = [d.value for d in self.files.date_tree.range_search(start, end) if d.value.user_id == self.current_user.id]
        if not all_trans:
            print("⚠️ No transactions found in this range.")
            return

        # Calcular ingresos y deducciones
        total_income = sum(t.amount for t in all_trans if t.is_income == 1)
        total_deductions = sum(t.amount for t in all_trans if t.is_deductible == 1 and t.is_income == 0)
        net_income = total_income - total_deductions

        print(f"\n💰 Total Income: ${total_income:,.2f}")
        print(f"🧾 Total Deductions: ${total_deductions:,.2f}")
        print(f"➡️ Net Taxable Income: ${net_income:,.2f}\n")

        if net_income <= 0:
            print("✅ No taxable income in this range (no ISR applied).")
            return

        # Buscar en tabla ISR con búsqueda binaria
        lim_inf, lim_sup, cuota_fija, porcentaje = self.files.buscar_isr_en_tabla(net_income)
        impuesto = cuota_fija + ((net_income - lim_inf) * (porcentaje / 100))
        tasa_efectiva = (impuesto / net_income) * 100

        print("📊 ISR Calculation:")
        print(f"  Range: ${lim_inf:,.2f} – ${lim_sup:,.2f}")
        print(f"  Fixed Quota: ${cuota_fija:,.2f}")
        print(f"  Rate: {porcentaje:.2f}% on excess over ${lim_inf:,.2f}")
        print(f"  💵 ISR to pay: ${impuesto:,.2f}")
        print(f"  📈 Effective tax rate: {tasa_efectiva:.2f}%\n")

# ================================================ EJECUCIÓN ================================================
S = System()
while True: # Login
    print("\n\n\n\n=============== Login ===============")
    enter = S.login(int(input("Enter your ID: ")), input("Enter your Password: "))
    if enter == True: break
    else:
        if int(input("0. Exit or 1. Retry: ")) == 0:
            print("\n.....................leaving the system, see you later.....................\n\n\n")
            break
while enter is True: # Options
    op = S.show_menu()
    if op == 1: S.register_transaction()
    elif op == 2: S.view_transaction()
    elif op == 3: S.modify_transaction()
    elif op == 4: S.delete_transaction()
    elif op == 5: S.generate_report()
    elif op == 6: S.calculate_taxes()
    elif op == 7:
        S.logout()
        break
    else: print("Invalid option.")