import os
import json
from datetime import datetime

class User: # sip
    def __init__(self, user_id, name, password):
        self.id = user_id
        self.name = name
        self.password = password

class Transaction: # sip
    def __init__(self, trans_id, user_id, amount, category, date, is_deductible, is_income, description):
        self.id = trans_id
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.date = date
        self.is_deductible = is_deductible
        self.is_income = is_income
        self.description = description

class Data: # sip
    def __init__(self, key, value):
        self.key = key
        self.value = value

class BTreeNode: # sip
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
        i = 0

        while i < self.n and self.keys[i].key < min_key:
            if not self.leaf and self.C[i]:
                self.C[i].range_search(min_key, max_key, result_list)
            i += 1

        while i < self.n and self.keys[i].key <= max_key:
            if not self.leaf and self.C[i]:
                self.C[i].range_search(min_key, max_key, result_list)
            result_list.append(self.keys[i])
            i += 1

        if not self.leaf and i < len(self.C) and self.C[i]:
            self.C[i].range_search(min_key, max_key, result_list)

    def exact_search(self, key, result_list):
        i = 0
        while i < self.n and key > self.keys[i].key:
            i += 1

        if not self.leaf and self.C[i]:
            self.C[i].exact_search(key, result_list)

        if i < self.n and self.keys[i] and self.keys[i].key == key:
            result_list.append(self.keys[i])

        if not self.leaf and i + 1 < len(self.C) and self.C[i + 1]:
            self.C[i + 1].exact_search(key, result_list)

class BTree: # sip
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
        result_list = []
        if self.root:
            self.root.range_search(min_key, max_key, result_list)
        return result_list

    def exact_search(self, key):
        result_list = []
        if self.root:
            self.root.exact_search(key, result_list)
        return result_list

class FileController:
    def __init__(self): # sip
        self.users_file = "users.json"
        self.transactions_file = "transactions.json"
        self.transaction_tree = BTree(2)
        self.users_tree = BTree(2)
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.deductible_tree = BTree(2)
        self.income_tree = BTree(2)
        self.current_user_id = None
        self._load_users_to_btree()
        self._initialize_files()
        self._load_transactions_to_btree()

    def _load_users_to_btree(self): # sip
        users = self.load_json(self.users_file)
        for u in users:
            try:
                user_obj = User(u["id"], u["name"], u["password"])
                self.users_tree.insert(Data(user_obj.id, user_obj))
            except Exception:
                continue

    def _initialize_files(self): # sip
        for file in [self.users_file, self.transactions_file]:
            if not os.path.exists(file):
                with open(file, "w", encoding="utf-8") as f:
                    json.dump([], f)
            else:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        json.load(f)
                except (json.JSONDecodeError, ValueError):
                    print(f"\n\t\t\t\t!!!!! {file} was corrupted. Reinitializing...")
                    with open(file, "w", encoding="utf-8") as f:
                        json.dump([], f)

    def load_json(self, file): # sip
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            with open(file, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def save_json(self, file, data): # sip
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def verify_user(self, user_id, password): # sip
        node = self.users_tree.search(user_id)
        if node and node.value.password == password:
            return node.value
        return None

    def get_next_id(self): # sip
        transactions = self.load_json(self.transactions_file)
        if not transactions: return 1
        return max((t.get("id", 0) for t in transactions), default=0) + 1

    def save_transaction(self, transaction): # sip
        transactions = self.load_json(self.transactions_file)
        transactions.append({"id": transaction.id, "user_id": transaction.user_id, "amount": transaction.amount, "category": transaction.category, "date": transaction.date, "is_deductible": transaction.is_deductible, "is_income": transaction.is_income, "description": transaction.description})
        self.save_json(self.transactions_file, transactions)
        self.transaction_tree.insert(Data(transaction.id, transaction))

        if self.current_user_id is not None and transaction.user_id == self.current_user_id:
            self.amount_tree.insert(Data(transaction.amount, transaction))
            self.category_tree.insert(Data(transaction.category, transaction))
            self.date_tree.insert(Data(transaction.date, transaction))
            self.deductible_tree.insert(Data(transaction.is_deductible, transaction))
            self.income_tree.insert(Data(transaction.is_income, transaction))

    def _load_transactions_to_btree(self): # sip
        transactions = self.load_json(self.transactions_file)
        for t in transactions:
            try:
                obj = Transaction(t["id"], t["user_id"], t["amount"], t["category"], t["date"], t["is_deductible"], t["is_income"], t.get("description", ""))
                self.transaction_tree.insert(Data(obj.id, obj))
            except: continue

    def load_user_secondary_trees(self, user_id): # sip
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.deductible_tree = BTree(2)
        self.income_tree = BTree(2)

        transactions = self.load_json(self.transactions_file)
        for t in transactions:
            try:
                if t.get("user_id") == user_id:
                    obj = Transaction(t["id"], t["user_id"], t["amount"], t["category"], t["date"], t["is_deductible"], t["is_income"], t.get("description", ""))
                    self.amount_tree.insert(Data(obj.amount, obj))
                    self.category_tree.insert(Data(obj.category, obj))
                    self.date_tree.insert(Data(obj.date, obj))
                    self.deductible_tree.insert(Data(obj.is_deductible, obj))
                    self.income_tree.insert(Data(obj.is_income, obj))
            except: continue
        self.current_user_id = user_id

    def find_transaction(self, trans_id): # sip
        node = self.transaction_tree.search(trans_id)
        return node.value if node else None

    def update_transaction(self, trans_id, field, new_value): # sip
        transactions = self.load_json(self.transactions_file)
        updated = False
        for t in transactions:
            if t.get("id") == trans_id:
                t[field] = new_value
                updated = True
                break

        if updated:
            self.save_json(self.transactions_file, transactions)
            trans = self.find_transaction(trans_id)
            if trans:
                setattr(trans, field, new_value)

                if field in ["amount", "category", "date", "is_deductible", "is_income"]:
                    if self.current_user_id is not None:
                        self.load_user_secondary_trees(self.current_user_id)

        return updated

    def delete_transaction(self, trans_id): # sip
        transactions = self.load_json(self.transactions_file)
        new_data = [t for t in transactions if t.get("id") != trans_id]
        if len(new_data) == len(transactions):
            return False
        self.save_json(self.transactions_file, new_data)
        self.transaction_tree = BTree(2)
        self._load_transactions_to_btree()

        if self.current_user_id is not None:
            self.load_user_secondary_trees(self.current_user_id)
        return True

    def merge_sort(self, items, key="amount"):
        if len(items) <= 1:
            return items
        mid = len(items) // 2
        left = self.merge_sort(items[:mid], key)
        right = self.merge_sort(items[mid:], key)
        return self.merge(left, right, key)

    def merge(self, left, right, key): # sip
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

    def binary_search(self, income): # sip
        table = [(0.01, 746.04, 0.00, 1.92), (746.05, 6332.05, 14.32, 6.40), (6332.06, 11128.01, 371.83, 10.88), (11128.02, 12935.82, 893.63, 16.00), (12935.83, 15487.71, 1182.88, 17.92), (15487.72, 31236.49, 1640.18, 21.36), (31236.50, 49233.00, 5004.12, 23.52), (49233.01, 93993.90, 9236.89, 30.00), (93993.91, 125325.20, 22665.17, 32.00), (125325.21, 375975.61, 32691.18, 34.00), (375975.62, float("inf"), 117912.32, 35.00)]
        left, right = 0, len(table) - 1

        while left <= right:
            mid = (left + right) // 2
            lower_limit, upper_limit, fixed_fee, percentage = table[mid]
            if lower_limit <= income <= upper_limit: return table[mid]
            elif income < lower_limit: right = mid - 1
            else: left = mid + 1
        return table[-1]

class System:
    def __init__(self): # sip
        self.files = FileController()
        self.current_user = None

    def login(self, user_id, password): # sip
        user = self.files.verify_user(user_id, password)
        print()
        if user:
            self.current_user = user
            self.files.load_user_secondary_trees(user.id)
            print(f"\n\t\t\t!!!!! Welcome {user.name} ¡¡¡¡¡\n")
            return True
        else:
            print("\n\t\t\t!!!!! Invalid user ID or password. !!!!!\n")
            return False

    def logout(self): # sip
        if self.current_user:
            print(f"\n\t\t\t!!!!! Logged out for {self.current_user.name} !!!!!\n\n")
            self.current_user = None
            self.files.amount_tree = BTree(2)
            self.files.category_tree = BTree(2)
            self.files.date_tree = BTree(2)
            self.files.deductible_tree = BTree(2)
            self.files.income_tree = BTree(2)
            self.files.current_user_id = None

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
        except:
            print("\n\t\t\t!!!!! Invalid input. Please enter a number. !!!!!\n")
            option = 0
        return option

    def register_transaction(self): # sip
        if not self.current_user:
            print("\n\t\t\t!!!!! You must log in first. !!!!!\n")
            return
        print("\n========== REGISTER NEW TRANSACTION ==========")
        while True:
            try:
                amount_input = input("Amount: ")
                amount = float(amount_input)
                if amount <= 0:
                    print("\n\t\t\t!!!!! Amount must be greater than 0. !!!!!\n")
                    continue
                break
            except:
                print("\n\t\t\t!!!!! Invalid input. Please enter a numeric amount. !!!!!\n")

        while True:
            try:
                is_deductible_input = input("Is deductible? (0 -> No, 1 -> Yes): ")
                is_deductible = int(is_deductible_input)
                if is_deductible not in [0, 1]:
                    print("\n\t\t\t!!!!! Invalid option. Please enter 0 or 1. !!!!!\n")
                    continue
                break
            except:
                print("\n\t\t\t!!!!! Invalid input. Please enter numbers only. !!!!!\n")

        while True:
            try:
                is_income_input = input("Is income? (0 -> Expense, 1 -> Income): ")
                is_income = int(is_income_input)
                if is_income not in [0, 1]:
                    print("\n\t\t\t!!!!! Invalid option. Please enter 0 or 1. !!!!!\n")
                    continue
                break
            except:
                print("\n\t\t\t!!!!! Invalid input. Please enter numbers only. !!!!!\n")

        categories = ["Salary", "Donation", "Investment", "Housing", "Food", "Health", "Transport", "Education", "Debts", "Other"]
        print("\nAvailable Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        while True:
            try:
                cat_choice_input = input("Select category: ")
                cat_choice = int(cat_choice_input)
                if cat_choice < 1 or cat_choice > len(categories):
                    print("\n\t\t\t!!!!! Invalid category number. !!!!!\n")
                    continue
                category = categories[cat_choice - 1]
                break
            except:
                print("\n\t\t\t!!!!! Invalid input. Please enter a number. !!!!!\n")

        description = input("Description: ").strip()
        if not description:
            print("\n\t\t\t!!!!! Empty description. Transaction will be saved without description. !!!!!\n")

        trans_id = self.files.get_next_id()
        date = datetime.now().strftime("%Y-%m-%d")
        new_trans = Transaction(trans_id, self.current_user.id, amount, category, date, is_deductible, is_income, description)
        self.files.save_transaction(new_trans)
        print(f"\n\t\t\t!!!!! Transaction #{trans_id} registered successfully. !!!!!\n")

    def view_transaction(self): # sip
        print("\n========== VIEW TRANSACTION ==========")
        while True:
            try:
                trans_id_input = input("Enter transaction ID: ")
                trans_id = int(trans_id_input)
                break
            except:
                print("\n\t\t\t!!!!! Invalid ID. Please enter a number. !!!!!\n")
        
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("\n\t\t\t!!!!! Transaction not found or unavailable. !!!!!\n")
            return
        print(f"\n========== Transaction #{trans.id} ========== \n\tCategory: {trans.category}\n\tAmount: ${trans.amount}\n\tDate: {trans.date}\n\tDeductible: {'Yes' if trans.is_deductible else 'No'}\n\tType: {'Income' if trans.is_income else 'Expense'}\n\tDescription: {trans.description} \n========================================")

    def modify_transaction(self): # sip
        print("\n========== MODIFY TRANSACTION ==========")
        while True:
            try:
                trans_id_input = input("Enter transaction ID: ")
                trans_id = int(trans_id_input)
                break
            except:
                print("\n\t\t\t!!!!! Invalid ID. Please enter a number. !!!!!\n")
        
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("\n\t\t\t!!!!! Transaction not found or unavailable. !!!!!\n")
            return

        while True:
            print("\nSelect field to modify:\n1. Amount\n2. Is Deductible\n3. Is Income\n4. Category\n5. Description\n6. Exit")
            try:
                op_input = input("Option: ")
                op = int(op_input)
            except:
                print("\n\t\t\t!!!!! Invalid input. Please enter a number. !!!!!\n")
                continue
            
            if op == 6:
                break
                
            field_map = {1: "amount", 2: "is_deductible", 3: "is_income", 4: "category", 5: "description"}
            field = field_map.get(op)
            if not field:
                print("\n\t\t\t!!!!! Invalid option. Please enter a number between 1 and 6. !!!!!\n")
                continue

            new_value = input(f"Enter new value for {field}: ")
            
            if field == "amount":
                while True:
                    try:
                        new_value_f = float(new_value)
                        if new_value_f <= 0:
                            print("\n\t\t\t!!!!! Amount must be greater than 0. !!!!!\n")
                            new_value = input(f"Enter new value for {field}: ")
                            continue
                        new_value = new_value_f
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid number. !!!!!\n")
                        new_value = input(f"Enter new value for {field}: ")
                        
            elif field in ["is_deductible", "is_income"]:
                while True:
                    try:
                        new_value_i = int(new_value)
                        if new_value_i not in [0, 1]:
                            print("\n\t\t\t!!!!! Must be 0 or 1. !!!!!\n")
                            new_value = input(f"Enter new value for {field}: ")
                            continue
                        new_value = new_value_i
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. Enter 0 or 1. !!!!!\n")
                        new_value = input(f"Enter new value for {field}: ")
                        
            elif field == "category":
                categories = ["Salary", "Donation", "Investment", "Housing", "Food", "Health", "Transport", "Education", "Debts", "Other"]
                while True:
                    try:
                        new_idx = int(new_value)
                        if new_idx < 1 or new_idx > len(categories):
                            print("\n\t\t\t!!!!! Invalid category number. !!!!!\n")
                            new_value = input(f"Enter new value for {field}: ")
                            continue
                        new_value = categories[new_idx - 1]
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. Please enter a number corresponding to category. !!!!!\n")
                        new_value = input(f"Enter new value for {field}: ")

            if self.files.update_transaction(trans_id, field, new_value):
                print("\n\t\t\t!!!!! Field updated successfully. !!!!!\n")
            else:
                print("\n\t\t\t!!!!! Update failed. !!!!!\n")

    def delete_transaction(self): # sip
        print("\n========== DELETE TRANSACTION ==========")
        while True:
            try:
                trans_id_input = input("Enter transaction ID to delete: ")
                trans_id = int(trans_id_input)
                break
            except:
                print("\n\t\t\t!!!!! Invalid ID. Please enter a number. !!!!!\n")
        
        trans = self.files.find_transaction(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print("\n\t\t\t!!!!! Transaction not found or unavailable. !!!!!\n")
            return

        if self.files.delete_transaction(trans_id): print(f"\n\t\t\t!!!!! Transaction #{trans_id} deleted successfully. !!!!!\n")
        else: print("\n\t\t\t!!!!! Transaction not found. !!!!!\n")

    def generate_report(self): # sip
        if not self.current_user:
            print("\n\t\t\t!!!!! You must log in first to generate a report. !!!!!\n")
            return

        all_trans = self.files.transaction_tree.traverse()
        if not all_trans:
            print("\n\t\t\t!!!!! There are no transactions available to report. !!!!!\n")
            return

        print("\n========== GENERATE REPORT ==========")
        print("You can filter transactions by multiple criteria.\n")

        all_results = None
        applied_filters = []
        combined_title = []

        while True:
            print("\nSelect a filter criterion:\n1. Amount range\n2. Category\n3. Date range\n4. Is Deductible\n5. Is Income\n7. Undo last filter\n6. Done (generate report)")

            while True:
                try:
                    op_input = input("Option: ")
                    op = int(op_input)
                    break
                except:
                    print("Invalid input.")

            if op == 6:
                break
            
            if op == 7:
                if not applied_filters:
                    print("\n\t\t\t!!!!! No filters to undo. !!!!!\n")
                    continue
                removed_filter = combined_title.pop()
                applied_filters.pop()
                if applied_filters:
                    all_results = set.intersection(*applied_filters)
                else:
                    all_results = None
                print(f"\n\t\t\t!!!!! Filter undone: {removed_filter} !!!!!\n")
                if all_results:
                    print(f"\n\t\t\t!!!!! Remaining results: {len(all_results)} transactions !!!!!\n")
                else:
                    print("\n\t\t\t!!!!! No filters active now. !!!!!\n")
                continue

            current_set = set()
            title_part = ""

            if op == 1:
                while True:
                    try:
                        min_a_input = input("Minimum amount: ")
                        max_a_input = input("Maximum amount: ")
                        min_a = float(min_a_input)
                        max_a = float(max_a_input)
                        if max_a < min_a:
                            print("\n\t\t\t!!!!! Invalid range: maximum amount must be greater than or equal to minimum amount. !!!!!\n")
                            continue
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. Please enter numeric values. !!!!!\n")

                found = [d.value for d in self.files.amount_tree.range_search(min_a, max_a)]
                current_set = {t.id for t in found}
                title_part = f"Amount ${min_a}–${max_a}"

            elif op == 2:
                all_cats = sorted(list({d.key for d in self.files.category_tree.traverse()}))
                if not all_cats:
                    print("\n\t\t\t!!!!! No categories found for this user. !!!!!\n")
                    continue
                print("\nAvailable categories:")
                for i, cat in enumerate(all_cats, start=1):
                    print(f"{i}. {cat}")
                
                while True:
                    try:
                        selected_input = input("Select a category number: ")
                        selected = int(selected_input)
                        if selected < 1 or selected > len(all_cats):
                            print("\n\t\t\t!!!!! Invalid selection. !!!!!\n")
                            continue
                        cat = all_cats[selected - 1]
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. !!!!!\n")
                        
                found = [d.value for d in self.files.category_tree.exact_search(cat)]
                current_set = {t.id for t in found}
                title_part = f"Category '{cat}'"

            elif op == 3:
                while True:
                    start = input("From (YYYY-MM-DD): ")
                    end = input("To (YYYY-MM-DD): ")
                    try:
                        start_dt = datetime.strptime(start, "%Y-%m-%d")
                        end_dt = datetime.strptime(end, "%Y-%m-%d")
                        if end_dt < start_dt:
                            print("\n\t\t\t!!!!! Invalid range: end date must be the same or after start date. !!!!!\n")
                            continue
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid date format. Please use YYYY-MM-DD. !!!!!\n")

                found = [d.value for d in self.files.date_tree.range_search(start, end)]
                found = [t for t in found if t.user_id == self.current_user.id]
                current_set = {t.id for t in found}
                title_part = f"Dates {start}–{end}"

            elif op == 4:
                while True:
                    print("1. Only Deductible\n2. Only Not Deductible\n3. Both")
                    try:
                        sel_d_input = input("Select option: ")
                        sel_d = int(sel_d_input)
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. !!!!!\n")

                if sel_d == 1:
                    found = [d.value for d in self.files.deductible_tree.exact_search(1)]
                    current_set = {t.id for t in found}
                    title_part = "Deductible only"
                elif sel_d == 2:
                    found = [d.value for d in self.files.deductible_tree.exact_search(0)]
                    current_set = {t.id for t in found}
                    title_part = "Not deductible only"
                elif sel_d == 3:
                    found_yes = [d.value for d in self.files.deductible_tree.exact_search(1)]
                    found_no = [d.value for d in self.files.deductible_tree.exact_search(0)]
                    all_found = found_yes + found_no
                    current_set = {t.id for t in all_found}
                    title_part = "Both deductible and not deductible"
                else:
                    print("\n\t\t\t!!!!! Invalid selection. !!!!!\n")
                    continue

            elif op == 5:
                while True:
                    print("1. Income\n2. Expense\n3. Both")
                    try:
                        sel_input = input("Select type: ")
                        sel = int(sel_input)
                        if sel not in [1, 2, 3]:
                            print("\n\t\t\t!!!!! Invalid option. !!!!!\n")
                            continue
                        break
                    except:
                        print("\n\t\t\t!!!!! Invalid input. !!!!!\n")
                        
                if sel == 3:
                    found_income = [d.value for d in self.files.income_tree.exact_search(1)]
                    found_expense = [d.value for d in self.files.income_tree.exact_search(0)]
                    all_found = found_income + found_expense
                    current_set = {t.id for t in all_found}
                    title_part = "Both income and expense"
                else:
                    found = [d.value for d in self.files.income_tree.exact_search(1 if sel == 1 else 0)]
                    current_set = {t.id for t in found}
                    title_part = "Income" if sel == 1 else "Expense"

            else:
                print("\n\t\t\t!!!!! Invalid option. !!!!!\n")
                continue

            applied_filters.append(current_set)
            combined_title.append(title_part)

            if applied_filters:
                all_results = set.intersection(*applied_filters)
            else:
                all_results = current_set

            print(f"\n\t\t\t!!!!! Filter applied: {title_part} !!!!!\n")
            print(f"\n\t\t\t!!!!! Remaining results: {len(all_results)} transactions !!!!!\n")

            another = input("Add another filter? (y/n): ").strip().lower()
            if another != "y":
                break

        if not all_results:
            print("\n\t\t\t!!!!! No transactions found with the selected filters. !!!!!\n")
            return

        results = [d.value for d in self.files.transaction_tree.traverse() if d.value.id in all_results and d.value.user_id == self.current_user.id]
        results = self.files.merge_sort(results, "amount")

        print("\n\n========== Transaction Report ==========")
        for t in results:
            print(f"\nID: {t.id} | Category: {t.category} | Amount: ${t.amount} | Date: {t.date}")
            print(f"Deductible: {'Yes' if t.is_deductible else 'No'} | Type: {'Income' if t.is_income else 'Expense'}")
            print(f"Description: {t.description}")
            print("-" * 60)

        choice = input("\nGenerate a text report file? (y/n): ").strip().lower()
        if choice != "y":
            print("\n\t\t\t!!!!! Report generation canceled. !!!!!\n")
            return

        existing_reports = [f for f in os.listdir() if f.startswith("transaction report #")]
        report_num = len(existing_reports) + 1
        filename = f"transaction report #{report_num}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Transaction Report\n")
            f.write("Filters: " + ", ".join(combined_title) + "\n")
            f.write(f"User: {self.current_user.name}\n\n")
            for t in results:
                f.write(f"ID: {t.id}\nCategory: {t.category}\nAmount: ${t.amount}\nDate: {t.date}\n"
                        f"Description: {t.description}\nDeductible: {'Yes' if t.is_deductible else 'No'}\n"
                        f"Type: {'Income' if t.is_income else 'Expense'}\n")
                f.write("-" * 50 + "\n")

        print(f"\n\t\t\t!!!!! Report file generated successfully: {filename} !!!!!\n")

    def calculate_taxes(self): # sip
        if not self.current_user:
            print("\n\t\t\t!!!!! You must log in first. !!!!!\n")
            return
        
        print("\n========== CALCULATE TAXES (ISR) ==========")
        while True:
            start = input("Enter start date (YYYY-MM-DD): ")
            end = input("Enter end date (YYYY-MM-DD): ")
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                if end_dt < start_dt:
                    print("\n\t\t\t!!!!! Invalid range: end date must be after start date. !!!!!\n")
                    continue
                break
            except:
                print("\n\t\t\t!!!!! Invalid date format. Please use YYYY-MM-DD. !!!!!\n")

        found = [d.value for d in self.files.date_tree.range_search(start, end)]
        all_trans = [t for t in found if t.user_id == self.current_user.id]

        if not all_trans:
            print("\n\t\t\t!!!!! No transactions found in this range. !!!!!\n")
            return

        total_income = sum(t.amount for t in all_trans if t.is_income == 1)
        total_deductions = sum(t.amount for t in all_trans if t.is_deductible == 1 and t.is_income == 0)
        net_income = total_income - total_deductions

        print(f"\nTotal Income: ${total_income:,.2f}")
        print(f"\tTotal Deductions: ${total_deductions:,.2f}")
        print(f"\tNet Taxable Income: ${net_income:,.2f}\n")

        if net_income <= 0:
            print("\n\t\t\t!!!!! No taxable income in this range (no ISR applied). !!!!!\n")
            return

        lim_inf, lim_sup, cuota_fija, porcentaje = self.files.binary_search(net_income)
        impuesto = cuota_fija + ((net_income - lim_inf) * (porcentaje / 100))
        tasa_efectiva = (impuesto / net_income) * 100

        print("ISR Calculation:")
        print(f"\tRange: ${lim_inf:,.2f} – ${lim_sup:,.2f}")
        print(f"\tFixed Quota: ${cuota_fija:,.2f}")
        print(f"\tRate: {porcentaje:.2f}% on excess over ${lim_inf:,.2f}")
        print(f"\tISR to pay: ${impuesto:,.2f}")
        print(f"\tEffective tax rate: {tasa_efectiva:.2f}%\n")

        save = input("Generate ISR report file? (y/n): ").strip().lower()
        if save == "y":
            existing_reports = [f for f in os.listdir() if f.startswith("ISR report #")]
            report_num = len(existing_reports) + 1
            filename = f"ISR report #{report_num}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("ISR Report\n")
                f.write(f"User: {self.current_user.name}\n")
                f.write(f"Date range: {start} – {end}\n\n")
                f.write(f"Total Income: ${total_income:,.2f}\n")
                f.write(f"Total Deductions: ${total_deductions:,.2f}\n")
                f.write(f"Net Taxable Income: ${net_income:,.2f}\n\n")
                f.write(f"ISR Range: ${lim_inf:,.2f} – ${lim_sup:,.2f}\n")
                f.write(f"Fixed Quota: ${cuota_fija:,.2f}\n")
                f.write(f"Rate: {porcentaje:.2f}%\n")
                f.write(f"ISR to Pay: ${impuesto:,.2f}\n")
                f.write(f"Effective Tax Rate: {tasa_efectiva:.2f}%\n")
            print(f"\n\t\t\t!!!!! ISR report generated: {filename} !!!!!\n")

if __name__ == "__main__":
    S = System()
    while True:
        print("\n\n\n\n============================== Login ==============================\n")
        try: 
            user_id_input = input("Enter your ID: ")
            password = input("Enter your Password: ")
            enter = S.login(int(user_id_input), password)
        except:
            print("\n\t\t\t!!!!! Invalid ID format ¡¡¡¡¡\n")
            enter = False
            
        if enter == True:
            break
        else:
            try:
                retry_input = input("0 -> Exit or any -> Retry: ")
                if int(retry_input) == 0:
                    print("\n============================== Exiting the system, goodbye ==============================\n\n\n")
                    break
            except: 
                continue

    while enter:
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
        else: print("\n\t\t\t!!!!! Invalid option. Please try again. !!!!!\n")