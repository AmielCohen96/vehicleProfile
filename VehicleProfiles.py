class Node:
    def __init__(self, value=""):
        self.value = value
        self.children = {}


class LempelZivTree:
    def __init__(self):
        self.root = Node()

    def insert(self, s):
        current = self.root
        for char in s:
            if char not in current.children:
                current.children[char] = Node(current.value + char)
            current = current.children[char]

    def build_tree(self, s):
        i = 0
        while i < len(s):
            current = self.root
            j = i
            while j < len(s) and s[j] in current.children:
                current = current.children[s[j]]
                j += 1
            if j < len(s):
                self.insert(s[i:j + 1])
            i = j + 1

    def search(self, substring):
        current = self.root
        for char in substring:
            if char not in current.children:
                return False
            current = current.children[char]
        return True

    def display(self, node=None, level=0):
        if node is None:
            node = self.root
        print(" " * level + node.value)
        for child in node.children.values():
            self.display(child, level + 2)


class VehicleProfiles:
    def __init__(self):
        self.profiles = {}

    def add_trip(self, vehicle_id: str, trip: str):
        vehicle_id = str(vehicle_id)  # Ensure consistency in data type
        if vehicle_id not in self.profiles:
            self.profiles[vehicle_id] = {"trip_string": "", "tree": LempelZivTree()}
        self.profiles[vehicle_id]["trip_string"] += trip
        self.profiles[vehicle_id]["tree"].build_tree(self.profiles[vehicle_id]["trip_string"])

    def display_profile(self, vehicle_id: str):
        vehicle_id = str(vehicle_id)  # Ensure consistency in data type
        if vehicle_id in self.profiles:
            self.profiles[vehicle_id]["tree"].display()
        else:
            print(f"No profile found for vehicle number: {vehicle_id}")
