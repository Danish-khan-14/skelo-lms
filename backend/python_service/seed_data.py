import json
from database import get_connection, initialize_database

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM recommendations")
    cursor.execute("DELETE FROM student_ability")
    cursor.execute("DELETE FROM quiz_attempts")
    cursor.execute("DELETE FROM quiz_questions")
    cursor.execute("DELETE FROM topics")
    cursor.execute("DELETE FROM chapters")
    cursor.execute("DELETE FROM subjects")
    cursor.execute("DELETE FROM curriculums")

    cursor.execute("INSERT INTO curriculums (id, title, description) VALUES (1, 'Computer Science', 'Core CS curriculum')")

    subjects = [
        (1, 1, "Python", "Learn Python programming from scratch"),
        (2, 1, "Web Development", "Learn HTML, CSS and JavaScript"),
        (3, 1, "Data Structures", "Learn arrays, linked lists, trees and graphs"),
    ]
    cursor.executemany(
        "INSERT INTO subjects (id, curriculum_id, title, description) VALUES (?, ?, ?, ?)",
        subjects
    )

    chapters = [
        (1, 1, "Introduction to Python", "Basics of Python", 1),
        (2, 1, "Getting Started with Python", "Setup and first programs", 2),
        (3, 1, "Advanced Python", "Advanced concepts", 3),
        (4, 2, "HTML Basics", "Structure of web pages", 1),
        (5, 2, "CSS Styling", "Styling web pages", 2),
        (6, 2, "JavaScript Fundamentals", "Programming for the web", 3),
        (7, 3, "Arrays and Strings", "Basic data structures", 1),
        (8, 3, "Linked Lists and Stacks", "Linear data structures", 2),
        (9, 3, "Trees and Graphs", "Non-linear data structures", 3),
    ]
    cursor.executemany(
        "INSERT INTO chapters (id, subject_id, title, description, order_index) VALUES (?, ?, ?, ?, ?)",
        chapters
    )

    topics = [
        (1,  1, "Variables & Data Types",      "Learn Python variables",         "Easy",   1),
        (2,  1, "Basic Operators",              "Arithmetic and logical ops",     "Easy",   2),
        (3,  2, "Loops & Conditionals",         "For, while, if statements",      "Medium", 1),
        (4,  2, "Functions & Scope",            "Defining and calling functions", "Medium", 2),
        (5,  3, "OOP Concepts",                 "Classes and objects",            "Hard",   1),
        (6,  3, "Advanced Python Patterns",     "Generators and decorators",      "Hard",   2),
        (7,  4, "HTML Tags & Structure",        "Basic HTML elements",            "Easy",   1),
        (8,  4, "Forms & Inputs",               "HTML form elements",             "Easy",   2),
        (9,  5, "CSS Selectors & Properties",   "Styling with CSS",               "Medium", 1),
        (10, 5, "Flexbox & Grid",               "CSS layout systems",             "Medium", 2),
        (11, 6, "JS Variables & Functions",     "JavaScript basics",              "Hard",   1),
        (12, 6, "DOM Manipulation",             "Interacting with HTML via JS",   "Hard",   2),
        (13, 7, "Arrays & Searching",           "Array operations",               "Easy",   1),
        (14, 7, "Sorting Algorithms",           "Bubble, merge, quick sort",      "Easy",   2),
        (15, 8, "Linked Lists",                 "Singly and doubly linked lists", "Medium", 1),
        (16, 8, "Stacks & Queues",              "Stack and queue operations",     "Medium", 2),
        (17, 9, "Binary Trees",                 "Tree traversal algorithms",      "Hard",   1),
        (18, 9, "Graph Algorithms",             "BFS, DFS, shortest path",        "Hard",   2),
    ]
    cursor.executemany(
        "INSERT INTO topics (id, chapter_id, title, content_text, difficulty, order_index) VALUES (?, ?, ?, ?, ?, ?)",
        topics
    )

    questions = [
        (1,  "What is the output of print(type(1))?",                json.dumps(["<class 'int'>","<class 'str'>","<class 'float'>","<class 'bool'>"]),  "<class 'int'>",          "Easy"),
        (1,  "Which is a valid Python variable name?",               json.dumps(["2name","_name","name-1","name 1"]),                                    "_name",                  "Easy"),
        (1,  "What does len('hello') return?",                       json.dumps(["4","5","6","Error"]),                                                  "5",                      "Easy"),
        (2,  "What is the output of 3 ** 2?",                        json.dumps(["6","9","8","5"]),                                                      "9",                      "Easy"),
        (2,  "What is the output of bool(0)?",                       json.dumps(["True","False","0","None"]),                                            "False",                  "Easy"),
        (2,  "What does 10 % 3 return?",                             json.dumps(["3","1","0","2"]),                                                      "1",                      "Easy"),
        (3,  "What is the output of [x*2 for x in range(3)]?",       json.dumps(["[0,2,4]","[1,2,3]","[2,4,6]","[0,1,2]"]),                             "[0,2,4]",                "Medium"),
        (3,  "What does the 'pass' statement do?",                   json.dumps(["Exits loop","Does nothing","Skips iteration","Returns None"]),         "Does nothing",           "Medium"),
        (3,  "Which method removes last element of a list?",         json.dumps(["remove()","delete()","pop()","discard()"]),                            "pop()",                  "Medium"),
        (4,  "What does *args allow in a function?",                 json.dumps(["Keyword args","Variable positional args","Default values","Multiple returns"]), "Variable positional args", "Medium"),
        (4,  "What is a lambda function?",                           json.dumps(["Named function","Anonymous function","Class method","Built-in"]),      "Anonymous function",     "Medium"),
        (4,  "What is the output of list(range(2,10,3))?",           json.dumps(["[2,5,8]","[2,4,6,8]","[3,6,9]","[2,3,4]"]),                           "[2,5,8]",                "Medium"),
        (5,  "What does __slots__ do in a Python class?",            json.dumps(["Adds methods","Restricts instance attributes","Enables inheritance","Creates properties"]), "Restricts instance attributes", "Hard"),
        (5,  "Which correctly implements memoization?",              json.dumps(["@staticmethod","@classmethod","@functools.lru_cache","@property"]),    "@functools.lru_cache",   "Hard"),
        (5,  "What is the output of type(lambda: None).__name__?",   json.dumps(["function","lambda","NoneType","method"]),                             "function",               "Hard"),
        (6,  "What does the GIL prevent in Python?",                 json.dumps(["Memory leaks","True parallel thread execution","Async execution","Recursion"]), "True parallel thread execution", "Hard"),
        (6,  "What is the output of {**{'a':1}, **{'a':2}}?",        json.dumps(["{'a':1}","{'a':2}","{'a':1,'a':2}","Error"]),                         "{'a':2}",                "Hard"),
        (6,  "What is a generator expression vs list comprehension?",json.dumps(["Same thing","Generator is lazy list is eager","List is lazy","No difference"]), "Generator is lazy list is eager", "Hard"),
        (7,  "What tag is used for the largest heading in HTML?",     json.dumps(["<h6>","<h1>","<head>","<title>"]),                                    "<h1>",                   "Easy"),
        (7,  "Which tag creates a hyperlink?",                       json.dumps(["<link>","<a>","<href>","<url>"]),                                      "<a>",                    "Easy"),
        (7,  "What does the <br> tag do?",                           json.dumps(["Bold text","Line break","New paragraph","Horizontal rule"]),           "Line break",             "Easy"),
        (8,  "Which input type creates a checkbox?",                 json.dumps(["type='check'","type='box'","type='checkbox'","type='tick'"]),           "type='checkbox'",        "Easy"),
        (8,  "What attribute makes a form field required?",          json.dumps(["mandatory","required","must","validate"]),                             "required",               "Easy"),
        (9,  "Which CSS property changes text color?",               json.dumps(["font-color","text-color","color","foreground"]),                       "color",                  "Medium"),
        (9,  "What does 'display: flex' do?",                        json.dumps(["Hides element","Creates flex container","Makes element float","Centers element"]), "Creates flex container", "Medium"),
        (9,  "Which selector targets elements with class 'box'?",    json.dumps(["#box",".box","box","*box"]),                                           ".box",                   "Medium"),
        (10, "What is the default flex-direction?",                  json.dumps(["column","row-reverse","row","column-reverse"]),                        "row",                    "Medium"),
        (10, "Which property centers items in flexbox?",             json.dumps(["align-items: center","text-align: center","margin: auto","justify-content: center"]), "justify-content: center", "Medium"),
        (11, "What is the output of typeof null in JS?",             json.dumps(["null","undefined","object","string"]),                                 "object",                 "Hard"),
        (11, "What does === check in JavaScript?",                   json.dumps(["Value only","Type only","Value and type","Reference"]),                "Value and type",         "Hard"),
        (11, "What is a closure in JavaScript?",                     json.dumps(["A loop","Function with access to outer scope","A class","An array method"]), "Function with access to outer scope", "Hard"),
        (12, "Which method selects element by ID in JS?",            json.dumps(["querySelector","getElementsByClass","getElementById","getElement"]),  "getElementById",         "Hard"),
        (12, "What does addEventListener do?",                       json.dumps(["Removes event","Creates HTML element","Attaches event handler","Styles element"]), "Attaches event handler", "Hard"),
        (13, "What is the time complexity of binary search?",        json.dumps(["O(n)","O(n^2)","O(log n)","O(1)"]),                                   "O(log n)",               "Easy"),
        (13, "Which data structure uses FIFO order?",                json.dumps(["Stack","Queue","Tree","Graph"]),                                       "Queue",                  "Easy"),
        (13, "What is the time complexity of accessing array by index?", json.dumps(["O(n)","O(log n)","O(n^2)","O(1)"]),                               "O(1)",                   "Easy"),
        (14, "What is the best case of bubble sort?",                json.dumps(["O(n^2)","O(n log n)","O(n)","O(1)"]),                                  "O(n)",                   "Easy"),
        (14, "Which sort algorithm uses divide and conquer?",        json.dumps(["Bubble sort","Insertion sort","Merge sort","Selection sort"]),         "Merge sort",             "Easy"),
        (15, "What is the time complexity of linked list insertion at head?", json.dumps(["O(n)","O(log n)","O(1)","O(n^2)"]),                          "O(1)",                   "Medium"),
        (15, "Which pointer does a singly linked list node have?",   json.dumps(["prev","next and prev","next","head"]),                                 "next",                   "Medium"),
        (16, "Which data structure uses LIFO order?",                json.dumps(["Queue","Stack","Tree","Graph"]),                                       "Stack",                  "Medium"),
        (16, "What operation removes top element from stack?",       json.dumps(["push","enqueue","pop","dequeue"]),                                     "pop",                    "Medium"),
        (16, "What is the time complexity of stack push?",           json.dumps(["O(n)","O(log n)","O(n^2)","O(1)"]),                                   "O(1)",                   "Medium"),
        (17, "What traversal visits root first?",                    json.dumps(["Inorder","Postorder","Preorder","Level order"]),                       "Preorder",               "Hard"),
        (17, "What is the height of a single node tree?",            json.dumps(["0","1","-1","2"]),                                                     "0",                      "Hard"),
        (17, "Which tree has left child < root < right child?",      json.dumps(["AVL Tree","Heap","Binary Search Tree","B-Tree"]),                      "Binary Search Tree",     "Hard"),
        (18, "What does BFS use internally?",                        json.dumps(["Stack","Queue","Array","Linked List"]),                                "Queue",                  "Hard"),
        (18, "What does DFS use internally?",                        json.dumps(["Queue","Stack","Array","Heap"]),                                       "Stack",                  "Hard"),
        (18, "What is Dijkstra's algorithm used for?",               json.dumps(["Sorting","Shortest path","Tree traversal","Searching"]),               "Shortest path",          "Hard"),
        (18, "What is the time complexity of BFS?",                  json.dumps(["O(V)","O(E)","O(V+E)","O(V*E)"]),                                      "O(V+E)",                 "Hard"),
    ]
    cursor.executemany(
        "INSERT INTO quiz_questions (topic_id, question, options, answer, difficulty) VALUES (?, ?, ?, ?, ?)",
        questions
    )

    conn.commit()
    conn.close()
    print(f"Seeded 3 subjects, 9 chapters, 18 topics and {len(questions)} quiz questions successfully")

if __name__ == "__main__":
    initialize_database()
    seed_data()