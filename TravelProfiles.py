class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_trip = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, trip: str):
        node = self.root
        for char in trip:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_trip = True

    def search(self, trip: str) -> bool:
        node = self.root
        for char in trip:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_trip

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def display(self, node=None, prefix=''):
        if node is None:
            node = self.root
        if node.is_end_of_trip:
            print(f"Trip: {prefix}")
        for char, child_node in node.children.items():
            self.display(child_node, prefix + char)


class TravelProfiles:
    def __init__(self):
        self.profiles = {}

    def add_trip(self, vehicle_id: str, trip: str):
        if vehicle_id not in self.profiles:
            self.profiles[vehicle_id] = Trie()
        self.profiles[vehicle_id].insert(trip)

    def is_trip_in_profile(self, vehicle_id: str, trip: str) -> bool:
        if vehicle_id in self.profiles:
            return self.profiles[vehicle_id].search(trip)
        return False

    def is_trip_prefix_in_profile(self, vehicle_id: str, prefix: str) -> bool:
        if vehicle_id in self.profiles:
            return self.profiles[vehicle_id].starts_with(prefix)
        return False

    def display_profile(self, vehicle_id: str):
        if vehicle_id in self.profiles:
            self.profiles[vehicle_id].display()
        else:
            print(f"No profile found for vehicle number: {vehicle_id}")
