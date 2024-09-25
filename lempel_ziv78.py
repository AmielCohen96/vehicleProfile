class Node:
    def __init__(self, value=""):  # Corrected from _init_ to __init__
        self.value = value
        self.children = {}
        self.probability = 0.0  # Probability of the node
        self.weight = 0.0  # Derived weight based on leaf ratio
        self.leaf_count = 0  # Leaf count
        self.total_descendants = 0  # Total nodes under this node


class LempelZivTree:
    def __init__(self):  # Corrected from _init_ to __init__
        self.root = Node()
        self.leaves_count = 0  # Total leaves
        self.options = set()  # Set of options initialized with letters a to z
        self.total_nodes = 0  # Total nodes in the tree


    def count_all_children(self, node):
        count = 0
        for child in node.children.values():
            count += 1 + self.count_all_children(child)
        return count

    def is_leaf(self, node):
        return not node.children

    def count_leaves(self, node):
        if self.is_leaf(node):
            node.leaf_count = 1  # עלה נחשב לעצמו כעלה אחד
            return 1
        leaf_sum = 0
        for child in node.children.values():
            leaf_sum += self.count_leaves(child)
        node.leaf_count = leaf_sum
        return leaf_sum

    def add_options_to_leaves(self):
        self.leaves_count = 0
        self._add_options_to_node(self.root)

    def _add_options_to_node(self, node):
        for option in self.options:
            if option not in node.children:
                node.children[option] = Node(option)
                if self.is_leaf(node.children[option]):
                    self.leaves_count += 1
            else:
                self._add_options_to_node(node.children[option])

    def insert(self, s):
        current = self.root
        for char in s:
            if char not in current.children:
                # הוספת האפשרויות הישירות מהשורש
                if current == self.root:
                    self.options.add(char)
                # יצירת צומת חדש
                current.children[char] = Node(char)
                self.total_nodes += 1  # להוסיף לספירת הצמתים הכללית
            current = current.children[char]
            # עדכון מספר הצמתים שתחת כל צומת
            current.total_descendants += 1

    def build_tree(self, s):
        i = 0
        while i < len(s):
            current = self.root
            j = i
            # למצוא את הפריפיקס הארוך ביותר שכבר קיים בעץ
            while j < len(s) and s[j] in current.children:
                current = current.children[s[j]]
                j += 1
            # הוספת המחרוזת החדשה לעץ
            self.insert(s[i:j + 1])
            i = j + 1

        self.add_options_to_leaves()

    def calculate_weights(self, node=None, parent_leaf_count=None):
        if node is None:
            node = self.root
            self.count_leaves(node)  # נחשב את מספר העלים עבור כל צומת לפני חישוב המשקלות
            parent_leaf_count = self.leaves_count  # השורש יהיה צומת האב הראשון

        if self.is_leaf(node):
            # אם הצומת הוא עלה, נחשב את המשקל כ-1 חלקי מספר העלים של צומת האב
            node.weight = 1 / parent_leaf_count if parent_leaf_count > 0 else 0
        else:
            node.weight = node.leaf_count / parent_leaf_count if parent_leaf_count > 0 else 0
            for child in node.children.values():
                self.calculate_weights(child, node.leaf_count)  # עבור לכל ילד עם מספר העלים של הצומת הנוכחי כאב

    def calculate_sequence_probability(self, s):
        current = self.root
        probability = 10000.0  # נתחיל עם הסתברות של 1 (הסתברות ראשונית)
        for char in s:
            if char in current.children:
                current = current.children[char]
                probability *= current.weight
            else:
                current = self.root  # אם הסימבול לא נמצא, ההסתברות לרצף היא 0
                if char in current.children:
                    current = current.children[char]
                    if current.total_descendants > 0:
                        probability *= current.weight
        return probability

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        num_children = self.count_all_children(node)
        print(
            f"{'  ' * level}symbol {node.value} (num_child = {num_children}), weight = {node.weight}, leaf_count = {node.leaf_count}")
        for child in node.children.values():
            self.print_tree(child, level + 1)

    def print_summary(self):
        # סה"כ עלים
        print(f"Total number of leaves: {self.leaves_count}")

        # סה"כ ילדים לשורש
        root_children_count = len(self.root.children)
        print(f"Total number of children of the root: {root_children_count}")

        # כמה ילדים יש לכל ילד ישיר של השורש
        print("Number of children for each direct child of the root:")
        for child in self.root.children.values():
            child_children_count = self.count_all_children(child)
            print(f"Child '{child.value}' has {child_children_count} children.")



# דוגמה לשימוש
tree = LempelZivTree()
tree.build_tree("aabdbbacbbda")

# חישוב המשקלים
tree.calculate_weights()

# הדפסת מבנה העץ עם המשקלים
tree.print_tree()

# הדפסת הסיכום
tree.print_summary()

# חישוב הסתברות למחרוזת מסוימת
sequence_probability = tree.calculate_sequence_probability("bdca")
print(f"The probability of the sequence 'bdca' is: {sequence_probability}")