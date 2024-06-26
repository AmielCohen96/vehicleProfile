
class Node:
    def __init__(self, value=""):
        self.value = value
        self.children = {}
        self.probability = 0.0  # Adding a probability field
        self.counter = 1
        self.weight = 0.0

class LempelZivTree:
    def __init__(self):
        self.root = Node()
        self.leaves_count = 1  # Start with 1 because the root is initially considered a leaf
        self.options = []

    def insert(self, s):
        current = self.root
        for char in s:
            if char not in self.options:
                self.options.append(char)
            if char not in current.children:
                if not current.children:  # Current node is a leaf before adding a new child
                    self.leaves_count -= 1
                    current.counter -= 1
                current.children[char] = Node(char)
            current = current.children[char]
        if not current.children:  # Current node is a leaf after adding a new child
            self.leaves_count += 1

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

    def compute_probabilities(self):
        def compute_node_probabilities(node):
            if not node.children:  # If the node is a leaf
                node.probability = 1.0 / self.leaves_count
            else:
                node.probability = 0.0
                for child in node.children.values():
                    compute_node_probabilities(child)  # Compute probabilities for the child nodes
                    node.probability += child.probability  # Sum the probabilities of the child nodes
                    node.counter += child.counter
        compute_node_probabilities(self.root)

    def display(self, node=None, level=0):
        if node is None:
            node = self.root
        print(" " * level + f"{node.value} (probability: {node.probability:.4f}) (counter: {node.counter:.4f})")
        for child in node.children.values():
            self.display(child, level + 4)

class VehicleProfiles:
    def __init__(self):
        self.profiles = {}

    def add_trip(self, vehicle_id: str, trip: str):
        vehicle_id = str(vehicle_id)  # Ensure consistency in data type
        if vehicle_id not in self.profiles:
            self.profiles[vehicle_id] = {"trip_string": "", "tree": LempelZivTree()}
        self.profiles[vehicle_id]["trip_string"] += trip
        self.profiles[vehicle_id]["tree"].build_tree(self.profiles[vehicle_id]["trip_string"])
        self.profiles[vehicle_id]["tree"].compute_probabilities()

    def display_profile(self, vehicle_id: str):
        vehicle_id = str(vehicle_id)  # Ensure consistency in data type
        if vehicle_id in self.profiles:
            self.profiles[vehicle_id]["tree"].display()
        else:
            print(f"No profile found for vehicle number: {vehicle_id}")



