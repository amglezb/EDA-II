import os
import json
from datetime import datetime

class User:
    def __init__(self, user_id, name, password):
        self.id = int(user_id)
        self.name = name
        self.password = password

class Transaction:
    def __init__(self, trans_id, user_id, amount, category, date, is_deductible, is_income, description):
        self.id = int(trans_id)
        self.user_id = int(user_id)
        self.amount = float(amount)
        self.category = int(category)
        self.date = date
        self.is_deductible = 1 if int(is_deductible) else 0
        self.is_income = 1 if int(is_income) else 0
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
            i += 1
            if self.C[i].n == 2 * self.t - 1:
                self.splitChild(i, self.C[i])
                if self.keys[i].key < data.key:
                    i += 1
            self.C[i].insertNonFull(data)

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
            if not self.leaf and self.C[i]:
                self.C[i].traverse(output_list)
            output_list.append(self.keys[i])
        if not self.leaf and self.C[self.n]:
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

    def range_search(self, min_key, max_key, result):
        i = 0
        while i < self.n and self.keys[i].key < min_key:
            if not self.leaf and self.C[i]:
                self.C[i].range_search(min_key, max_key, result)
            i += 1
        while i < self.n and self.keys[i].key <= max_key:
            if not self.leaf and self.C[i]:
                self.C[i].range_search(min_key, max_key, result)
            result.append(self.keys[i])
            i += 1
        if not self.leaf and i < len(self.C) and self.C[i]:
            self.C[i].range_search(min_key, max_key, result)

    def exact_search(self, key, result):
        i = 0
        while i < self.n and key > self.keys[i].key:
            i += 1
        if not self.leaf and self.C[i]:
            self.C[i].exact_search(key, result)
        if i < self.n and self.keys[i] and self.keys[i].key == key:
            result.append(self.keys[i])
        if not self.leaf and i + 1 < len(self.C) and self.C[i + 1]:
            self.C[i + 1].exact_search(key, result)

class BTree:
    def __init__(self, t=2):
        self.root = None
        self.t = t

    def traverse(self):
        output_list = []
        if self.root:
            self.root.traverse(output_list)
        return output_list

    def search(self, k):
        return None if self.root is None else self.root.search(k)

    def insert(self, data):
        if self.root is None:
            self.root = BTreeNode(self.t, True)
            self.root.keys[0] = data
            self.root.n = 1
            return
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
        result = []
        if self.root:
            self.root.range_search(min_key, max_key, result)
        return result

    def exact_search(self, key):
        result = []
        if self.root:
            self.root.exact_search(key, result)
        return result

    def get_max(self):
        if self.root is None:
            return None
        current = self.root
        while not current.leaf:
            current = current.C[current.n]
        return current.keys[current.n - 1]

class FileController:
    cats = [None, "Salary", "Donation", "Investment", "Housing", "Food", "Health", "Transport", "Education", "Debts", "Other"]

    def __init__(self):
        self.users_file = "users.json"
        self.transactions_file = "transactions.json"
        self.transaction_tree = BTree(2)
        self.users_tree = BTree(2)
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.deductible_tree = BTree(2)
        self.income_tree = BTree(2)
        self.user_date_tree = BTree(2)
        self.current_user_id = None
        self.import_users()
        self.import_txns()

    def category_name(self, index):
        try:
            idx = int(index)
            if 1 <= idx < len(self.cats):
                return self.cats[idx]
        except: pass
        return "Unknown"

    def user_verification(self, user_id, password):
        node = self.users_tree.search(int(user_id))
        if node and node.value.password == password: return node.value
        return None

    def import_txns(self):
        transactions = self.read_json(self.transactions_file)
        for t in transactions:
            try:
                obj = Transaction(t["id"], t["user_id"], t["amount"], t["category"], t["date"], t.get("is_deductible", 0), t.get("is_income", 0), t.get("description", ""))
                self.transaction_tree.insert(Data(obj.id, obj))
            except: continue

    def import_users(self):
        users = self.read_json(self.users_file)
        for u in users:
            try:
                user_obj = User(u["id"], u["name"], u["password"])
                self.users_tree.insert(Data(user_obj.id, user_obj))
            except: continue

    def read_json(self, file):
        try:
            if not os.path.exists(file):
                with open(file, "w", encoding="utf-8") as f:
                    json.dump([], f)
                return []
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            with open(file, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []

    def save_json(self, file, data):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def secondary_trees(self, user_id):
        self.amount_tree = BTree(2)
        self.category_tree = BTree(2)
        self.date_tree = BTree(2)
        self.deductible_tree = BTree(2)
        self.income_tree = BTree(2)
        self.user_date_tree = BTree(2)
        all_tx = [d.value for d in self.transaction_tree.traverse()]
        for obj in all_tx:
            if obj.user_id == int(user_id):
                self.amount_tree.insert(Data(obj.amount, obj))
                self.category_tree.insert(Data(obj.category, obj))
                self.date_tree.insert(Data(obj.date, obj))
                self.deductible_tree.insert(Data(obj.is_deductible, obj))
                self.income_tree.insert(Data(obj.is_income, obj))
                date_key = f"{obj.date}_{obj.id:08d}"
                self.user_date_tree.insert(Data(date_key, obj))
        self.current_user_id = int(user_id)

    def new_id(self):
        max_node = self.transaction_tree.get_max()
        if max_node is None: return 1
        return max_node.value.id + 1

    def save_txn(self, transaction):
        transactions = self.read_json(self.transactions_file)
        transactions.append({"id": transaction.id, "user_id": transaction.user_id, "amount": transaction.amount, "category": transaction.category, "date": transaction.date, "is_deductible": transaction.is_deductible, "is_income": transaction.is_income, "description": transaction.description})
        self.save_json(self.transactions_file, transactions)
        self.transaction_tree.insert(Data(transaction.id, transaction))
        if self.current_user_id is not None and transaction.user_id == self.current_user_id:
            self.amount_tree.insert(Data(transaction.amount, transaction))
            self.category_tree.insert(Data(transaction.category, transaction))
            self.date_tree.insert(Data(transaction.date, transaction))
            self.deductible_tree.insert(Data(transaction.is_deductible, transaction))
            self.income_tree.insert(Data(transaction.is_income, transaction))
            date_key = f"{transaction.date}_{transaction.id:08d}"
            self.user_date_tree.insert(Data(date_key, transaction))

    def search_specific_txn(self, trans_id):
        node = self.transaction_tree.search(int(trans_id))
        return node.value if node else None

    def update_txn(self, trans_id, field, new_value):
        transactions = self.read_json(self.transactions_file)
        updated = False
        for t in transactions:
            if t.get("id") == int(trans_id):
                if field == "category":
                    t[field] = int(new_value)
                elif field in ("amount",):
                    t[field] = float(new_value)
                elif field in ("is_deductible", "is_income"):
                    t[field] = 1 if int(new_value) else 0
                else:
                    t[field] = new_value
                updated = True
                break
        if not updated:
            return False
        self.save_json(self.transactions_file, transactions)
        trans = self.search_specific_txn(trans_id)
        if trans:
            setattr(trans, field, t[field])
            if field in ["amount", "category", "date", "is_deductible", "is_income"] and self.current_user_id is not None:
                self.secondary_trees(self.current_user_id)
        return True

    def delete_txn(self, trans_id, user_id=None):
        node = self.transaction_tree.search(int(trans_id))
        if not node: return False

        txn = node.value
        if user_id is not None and txn.user_id != int(user_id): return False

        transactions = self.read_json(self.transactions_file)
        new_transactions = [t for t in transactions if t.get("id") != int(trans_id)]
        if len(new_transactions) == len(transactions): return False

        self.save_json(self.transactions_file, new_transactions)
        self.transaction_tree = BTree(2)
        self.import_txns()

        if self.current_user_id: self.secondary_trees(self.current_user_id)

        return True
    
    def merge_sort(self, items, key="amount"):
        if len(items) <= 1: return items
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

    def binary_search(self, income):
        table = [(0.01, 746.04, 0.00, 1.92), (746.05, 6332.05, 14.32, 6.40), (6332.06, 11128.01, 371.83, 10.88), (11128.02, 12935.82, 893.63, 16.00), (12935.83, 15487.71, 1182.88, 17.92), (15487.72, 31236.49, 1640.18, 21.36), (31236.50, 49233.00, 5004.12, 23.52), (49233.01, 93993.90, 9236.89, 30.00), (93993.91, 125325.20, 22665.17, 32.00), (125325.21, 375975.61, 32691.18, 34.00), (375975.62, float("inf"), 117912.32, 35.00)]
        left, right = 0, len(table) - 1
        while left <= right:
            mid = (left + right) // 2
            lower_limit, upper_limit, _, _ = table[mid]
            if lower_limit <= income <= upper_limit: return table[mid]
            elif income < lower_limit: right = mid - 1
            else: left = mid + 1
        return table[-1]

class System:
    def __init__(self):
        self.files = FileController()
        self.current_user = None

    def login(self, user_id, password):
        try: user = self.files.user_verification(user_id, password)
        except: return False
        if user:
            self.current_user = user
            self.files.secondary_trees(user.id)
            print(f"{'!!!!! Welcome ' + user.name + ' ¡¡¡¡¡':^100}")
            return True
        print(f"{'!!!!! Invalid user ID or password. !!!!!':^100}")
        return False

    def logout(self):
        if self.current_user:
            print(f"\n\n{'!!!!! Logged out for ' + self.current_user.name + ' !!!!!':^100}\n\n")
            self.current_user = None
            self.files.amount_tree = BTree(2)
            self.files.category_tree = BTree(2)
            self.files.date_tree = BTree(2)
            self.files.deductible_tree = BTree(2)
            self.files.income_tree = BTree(2)
            self.files.current_user_id = None

    def menu(self):
        print(f"\n{'='*100}\n{'MENU':^100}\n{'='*100}\n{'1. Register New Transaction':^100}\n{'2. View Transaction Data':^100}\n{'3. Modify Transaction Data':^100}\n{'4. Delete Transaction':^100}\n{'5. Generate Transaction Report':^100}\n{'6. Calculate Taxes (ISR)':^100}\n{'7. Logout':^100}\n{'='*100}")
        while True:
            try:
                op = int(input("Select an option: "))
                if 1 <= op <= 7: return op
                print(f"{'!!!!! Invalid option. Please enter a number between 1 and 7. !!!!!':^100}")
            except: print(f"{'!!!!! Invalid input. Please enter a number. !!!!!':^100}")

    def add_txn(self):
        if not self.current_user:
            print(f"{'!!!!! You must log in first. !!!!!':^100}")
            return
        while True:
            try:
                amount = float(input("Amount: "))
                if amount <= 0:
                    print(f"{'!!!!! Amount must be greater than 0. !!!!!':^100}")
                    continue
                break
            except: print(f"{'!!!!! Invalid input. Please enter a numeric amount. !!!!!':^100}")
        while True:
            deductible = input("Is deductible? (y/n): ").strip().lower()
            if deductible == "y":
                is_deductible = 1
                break
            if deductible == "n":
                is_deductible = 0
                break
            print(f"{'!!!!! Invalid option. Please enter y or n. !!!!!':^100}")
        while True:
            income = input("Is income? (y/n -> expense): ").strip().lower()
            if income == "y":
                is_income = 1
                break
            if income == "n":
                is_income = 0
                break
            print(f"{'!!!!! Invalid option. Please enter y or n. !!!!!':^100}")
        cats = FileController.cats[1:]
        print("\nAvailable cats:")
        for i, cat in enumerate(cats, 1):
            print(f"{i}. {cat}")
        while True:
            try:
                cat_choice = int(input("Select category: "))
                if cat_choice < 1 or cat_choice > len(cats):
                    print(f"{'!!!!! Invalid category number. !!!!!':^100}")
                    continue
                category = cat_choice
                break
            except: print(f"{'!!!!! Invalid input. Please enter a number. !!!!!':^100}")
        description = input("Description: ").strip()
        trans_id = self.files.new_id()
        date = datetime.now().strftime("%Y-%m-%d")
        new_trans = Transaction(trans_id, self.current_user.id, amount, category, date, is_deductible, is_income, description)
        self.files.save_txn(new_trans)
        print(f"{'!!!!! Transaction #' + str(trans_id) + ' registered successfully. !!!!!':^100}")

    def view_txn(self):
        print(f"\n{'='*100}\n{'VIEW TRANSACTION':^100}\n{'='*100}\n")
        while True:
            try:
                trans_id = int(input("Enter transaction ID: "))
                break
            except: print(f"{'!!!!! Invalid ID. Please enter a number. !!!!!':^100}")
        trans = self.files.search_specific_txn(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print(f"{'!!!!! Transaction not found or unavailable. !!!!!':^100}")
            return
        cat_name = self.files.category_name(trans.category)
        print(f"\n========== Transaction #{trans.id} ========== \n\tCategory: {cat_name}\n\tAmount: ${trans.amount}\n\tDate: {trans.date}\n\tDeductible: {'Yes' if trans.is_deductible else 'No'}\n\tType: {'Income' if trans.is_income else 'Expense'}\n\tDescription: {trans.description} \n========================================")

    def edit_txn(self):
        print(f"\n{'='*100}\n{'MODIFY TRANSACTION':^100}\n{'='*100}\n")
        while True:
            try:
                trans_id = int(input("Enter transaction ID: "))
                break
            except: print(f"{'!!!!! Invalid ID. Please enter a number. !!!!!':^100}")
        trans = self.files.search_specific_txn(trans_id)
        if not trans or trans.user_id != self.current_user.id:
            print(f"{'!!!!! Transaction not found or unavailable. !!!!!':^100}")
            return
        while True:
            print("\nSelect field to modify:\n1. Amount\n2. Is Deductible\n3. Is Income\n4. Category\n5. Description\n6. Exit")
            try:
                op = int(input("Option: "))
            except:
                print(f"{'!!!!! Invalid input. Please enter a number. !!!!!':^100}")
                continue
            if op == 6: break
            field_map = {1: "amount", 2: "is_deductible", 3: "is_income", 4: "category", 5: "description"}
            field = field_map.get(op)
            if not field:
                print(f"{'!!!!! Invalid option. Please enter a number between 1 and 6. !!!!!':^100}")
                continue
            if field == "amount":
                while True:
                    try:
                        new_value = float(input("Enter new amount: "))
                        if new_value <= 0:
                            print(f"{'!!!!! Amount must be greater than 0. !!!!!':^100}")
                            continue
                        break
                    except: print(f"{'!!!!! Invalid number. !!!!!':^100}")
                ok = self.files.update_txn(trans_id, field, new_value)
            elif field in ["is_deductible", "is_income"]:
                while True:
                    new_val = input(f"Enter new value for {field} (y/n): ").strip().lower()
                    if new_val == "y":
                        nv = 1
                        break
                    if new_val == "n":
                        nv = 0
                        break
                    print(f"{'!!!!! Invalid option. Please enter y or n. !!!!!':^100}")
                ok = self.files.update_txn(trans_id, field, nv)
            elif field == "category":
                cats = FileController.cats[1:]
                print("Available cats:")
                for i, cat in enumerate(cats, 1):
                    print(f"{i}. {cat}")
                while True:
                    try:
                        new_idx = int(input("Enter new category number: "))
                        if new_idx < 1 or new_idx > len(cats):
                            print(f"{'!!!!! Invalid category number. !!!!!':^100}")
                            continue
                        break
                    except: print(f"{'!!!!! Invalid input. Please enter a number corresponding to category. !!!!!':^100}")
                ok = self.files.update_txn(trans_id, field, new_idx)
            else:
                new_text = input(f"Enter new value for {field}: ")
                ok = self.files.update_txn(trans_id, field, new_text)
            if ok: print(f"{'!!!!! Field updated successfully. !!!!!':^100}")
            else: print(f"{'!!!!! Update failed. !!!!!':^100}")

    def delete_txn(self):
        print(f"\n{'='*100}\n{'DELETE TRANSACTION':^100}\n{'='*100}\n")
        while True:
            try:
                trans_id = int(input("Enter transaction ID to delete: "))
                break
            except: print(f"{'!!!!! Invalid ID. Please enter a number. !!!!!':^100}")

        ok = self.files.delete_txn(trans_id, self.current_user.id)
        if ok: print(f"{'!!!!! Transaction deleted successfully. !!!!!':^100}")
        else: print(f"{'!!!!! You can only delete your own transactions or the ID does not exist. !!!!!':^100}")

    def report(self):
        if not self.current_user:
            print(f"{'!!!!! You must log in first to generate a report. !!!!!':^100}")
            return
        all_trans = self.files.transaction_tree.traverse()
        if not all_trans:
            print(f"{'!!!!! There are no transactions available to report. !!!!!':^100}")
            return
        print(f"\n{'='*100}\n{'GENERATE REPORT':^100}\n{'='*100}\n")
        applied_filters = []
        combined_title = []
        all_results = None
        while True:
            print("Select a filter criterion:\n1. Amount range\n2. Category\n3. Date range\n4. Is Deductible\n5. Is Income\n6. Done (generate report)\n7. Undo last filter")
            try: op = int(input("Option: "))
            except:
                print(f"{'!!!!! Invalid input. !!!!!':^100}")
                continue
            if op == 6: break
            if op == 7:
                if not applied_filters:
                    print(f"{'!!!!! No filters to undo. !!!!!':^100}")
                    continue
                combined_title.pop()
                applied_filters.pop()
                all_results = set.intersection(*applied_filters) if applied_filters else None
                print(f"{'!!!!! Filter undone !!!!!':^100}")
                continue
            current_set = set()
            title_part = ""
            if op == 1:
                try:
                    min_a = float(input("Minimum amount: "))
                    max_a = float(input("Maximum amount: "))
                    if max_a < min_a:
                        print(f"{'!!!!! Invalid range: maximum amount must be greater than or equal to minimum amount. !!!!!':^100}")
                        continue
                except:
                    print(f"{'!!!!! Invalid input. Please enter numeric values. !!!!!':^100}")
                    continue
                found = [d.value for d in self.files.amount_tree.range_search(min_a, max_a)]
                current_set = {t.id for t in found}
                title_part = f"Amount ${min_a}–${max_a}"
            elif op == 2:
                all_cats = sorted(list({d.key for d in self.files.category_tree.traverse()}))
                if not all_cats:
                    print(f"{'!!!!! No cats found for this user. !!!!!':^100}")
                    continue
                print("\nAvailable cats:")
                for i, cat in enumerate(all_cats, start=1):
                    print(f"{i}. {self.files.category_name(cat)}")
                try: selected = int(input("Select a category number: "))
                except:
                    print(f"{'!!!!! Invalid input. !!!!!':^100}")
                    continue
                if selected < 1 or selected > len(all_cats):
                    print(f"{'!!!!! Invalid selection. !!!!!':^100}")
                    continue
                cat = all_cats[selected - 1]
                found = [d.value for d in self.files.category_tree.exact_search(cat)]
                current_set = {t.id for t in found}
                title_part = f"Category {self.files.category_name(cat)}"
            elif op == 3:
                start = input("From (YYYY-MM-DD): ")
                end = input("To (YYYY-MM-DD): ")
                try:
                    start_dt = datetime.strptime(start, "%Y-%m-%d")
                    end_dt = datetime.strptime(end, "%Y-%m-%d")
                    if end_dt < start_dt:
                        print(f"{'!!!!! Invalid range: end date must be the same or after start date. !!!!!':^100}")
                        continue
                except:
                    print(f"{'!!!!! Invalid date format. Please use YYYY-MM-DD. !!!!!':^100}")
                    continue
                found = [d.value for d in self.files.date_tree.range_search(start, end)]
                found = [t for t in found if t.user_id == self.current_user.id]
                current_set = {t.id for t in found}
                title_part = f"Dates {start}–{end}"
            elif op == 4:
                print("1. Only Deductible\n2. Only Not Deductible\n3. Both")
                try: sel_d = int(input("Select option: "))
                except:
                    print(f"{'!!!!! Invalid input. !!!!!':^100}")
                    continue
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
                    print(f"{'!!!!! Invalid selection. !!!!!':^100}")
                    continue
            elif op == 5:
                print("1. Income\n2. Expense\n3. Both")
                try: sel = int(input("Select type: "))
                except:
                    print(f"{'!!!!! Invalid input. !!!!!':^100}")
                    continue
                if sel == 3:
                    found_income = [d.value for d in self.files.income_tree.exact_search(1)]
                    found_expense = [d.value for d in self.files.income_tree.exact_search(0)]
                    all_found = found_income + found_expense
                    current_set = {t.id for t in all_found}
                    title_part = "Both income and expense"
                elif sel in (1, 2):
                    found = [d.value for d in self.files.income_tree.exact_search(1 if sel == 1 else 0)]
                    current_set = {t.id for t in found}
                    title_part = "Income" if sel == 1 else "Expense"
                else:
                    print(f"{'!!!!! Invalid option. !!!!!':^100}")
                    continue
            else:
                print(f"{'!!!!! Invalid option. !!!!!':^100}")
                continue
            applied_filters.append(current_set)
            combined_title.append(title_part)
            all_results = set.intersection(*applied_filters) if applied_filters else current_set
            print(f"{'!!!!! Filter applied: ' + title_part + ' !!!!!':^100}")
            print(f"{'!!!!! Remaining results: ' + str(len(all_results)) + ' transactions !!!!!':^100}")
            another = input("Add another filter? (y/n): ").strip().lower()
            if another != "y":
                break
        if not all_results:
            print(f"{'!!!!! No transactions found with the selected filters. !!!!!':^100}")
            return
        results = [d.value for d in self.files.transaction_tree.traverse() if d.value.id in all_results and d.value.user_id == self.current_user.id]
        results = self.files.merge_sort(results)
        print("\n\n========== Transaction Report ==========")
        for t in results:
            print(f"\nID: {t.id} | Category: {self.files.category_name(t.category)} | Amount: ${t.amount} | Date: {t.date}")
            print(f"Deductible: {'Yes' if t.is_deductible else 'No'} | Type: {'Income' if t.is_income else 'Expense'}")
            print(f"Description: {t.description}")
            print("-" * 60)
        choice = input("\nGenerate a text report file? (y/n): ").strip().lower()
        if choice != "y":
            print(f"{'!!!!! Report generation canceled. !!!!!':^100}")
            return
        existing_reports = [f for f in os.listdir() if f.startswith("transaction report #")]
        report_num = len(existing_reports) + 1
        filename = f"transaction report #{report_num}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Transaction Report\n")
            f.write("Filters: " + ", ".join(combined_title) + "\n")
            f.write(f"User: {self.current_user.name}\n\n")
            for t in results:
                f.write(f"ID: {t.id}\nCategory: {self.files.category_name(t.category)} ({t.category})\nAmount: ${t.amount}\nDate: {t.date}\nDescription: {t.description}\nDeductible: {'Yes' if t.is_deductible else 'No'}\nType: {'Income' if t.is_income else 'Expense'}\n")
                f.write("-" * 50 + "\n")
        print(f"{'!!!!! Report file generated successfully: ' + filename + ' !!!!!':^100}")

    def isr(self):
        if not self.current_user:
            print(f"{'!!!!! You must log in first. !!!!!':^70}")
            return
        print(f"\n{'='*100}\n{'CALCULATE TAXES (ISR)':^100}\n{'='*100}\n")
        while True:
            start = input("Enter start date (YYYY-MM-DD): ")
            end = input("Enter end date (YYYY-MM-DD): ")
            try:
                start_dt = datetime.strptime(start, "%Y-%m-%d")
                end_dt = datetime.strptime(end, "%Y-%m-%d")
                if end_dt < start_dt:
                    print(f"{'!!!!! Invalid range: end date must be after start date. !!!!!':^70}")
                    continue
                break
            except Exception:
                print(f"{'!!!!! Invalid date format. Please use YYYY-MM-DD. !!!!!':^70}")
        start_key = f"{start}_00000000"
        end_key = f"{end}_99999999"
        found = [d.value for d in self.files.user_date_tree.range_search(start_key, end_key)]
        if not found:
            print(f"{'!!!!! No transactions found in this range. !!!!!':^70}")
            return
        
        print(f"\n{'='*100}\n{'RESULTS':^100}\n{'='*100}\n")
        total_income = sum(t.amount for t in found if t.is_income == 1)
        total_deductions = sum(t.amount for t in found if t.is_deductible == 1 and t.is_income == 0)
        net_income = total_income - total_deductions
        print(f"\nTotal Income: ${total_income:,.2f}")
        print(f"Total Deductions: ${total_deductions:,.2f}")
        print(f"Net Taxable Income: ${net_income:,.2f}\n")
        if net_income <= 0:
            print(f"{'!!!!! No taxable income in this range (no ISR applied). !!!!!':^70}")
            return
        lim_inf, lim_sup, cuota_fija, porcentaje = self.files.binary_search(net_income)
        impuesto = cuota_fija + ((net_income - lim_inf) * (porcentaje / 100))
        tasa_efectiva = (impuesto / net_income) * 100
        print("ISR Calculation:")
        print(f"  Range: ${lim_inf:,.2f} – ${lim_sup:,.2f}")
        print(f"  Fixed Quota: ${cuota_fija:,.2f}")
        print(f"  Rate: {porcentaje:.2f}% on excess over ${lim_inf:,.2f}")
        print(f"  ISR to pay: ${impuesto:,.2f}")
        print(f"  Effective tax rate: {tasa_efectiva:.2f}%\n")

if __name__ == "__main__":
    S = System()
    while True:
        print(f"\n{'='*100}\n{'LOGIN':^100}\n{'='*100}\n")
        try:
            enter = S.login(int(input("Enter your ID: ")), input("Enter your Password: "))
        except Exception:
            print(f"{'!!!!! Invalid ID format ¡¡¡¡¡':^100}")
            enter = False
        if enter:
            break
        else:
            retry_input = input("Retry? (y/n) : ").strip().lower()
            if retry_input == "n":
                print(f"\n{'='*100}\n{'Exiting the system, goodbye':^100}\n{'='*100}\n\n")
                exit(0)
    while True:
        op = S.menu()
        if op == 1: S.add_txn()
        elif op == 2: S.view_txn()
        elif op == 3: S.edit_txn()
        elif op == 4: S.delete_txn()
        elif op == 5: S.report()
        elif op == 6: S.isr()
        elif op == 7:
            S.logout()
            break
        else: print(f"{'!!!!! Invalid option. Please try again. !!!!!':^100}")
