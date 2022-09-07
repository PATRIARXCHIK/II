import sys
from PIL import Image, ImageDraw
class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():

    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_stage(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Пустой фронтир")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("Пустой фронтир")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class Maze():

    # Прочитать файл и установить высоту и ширину лабиринта
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

    # Проверить начало и цель
        if contents.count("A") != 1:
           raise Exception("Лабиринт должен иметь ровно одну начальную точку")
        if contents.count("B") != 1:
           raise Exception("Лабиринт должен иметь ровно один финиш")

    # Определяем Высоту и ширину лабиринта
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

    # Слежка за стенами
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):
        row, col = state

        # Все возможные действия
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        # Убедиться, что действия допустимы
        result = []
        for action, (r,c) in candidates:
            try:
                if not self.walls[r][c]:
                    result.append((action, (r, c)))
            except IndexError:
                continue
        return result

    def solves(self):
        """Находит выход из лабиринта, если он существует"""

        # Слежка за кол-вом иследованных состояний
        self.num_explored = 0

        # Инициализируем границу только начальной позицией
        start = Node(state=self.start, parent=None, action=None)
        frontier = StackFrontier()
        frontier.add(start)

        # Инициализировать пустой иследуемый набор
        self.explored = set()

        # Продолжать цикл, пока не будет найдено решение
        while True:

            # Если ничего не осталось во фронтире, то пути неь
            if frontier.empty():
                raise Exception("Нет решения")

            # Выбираем узел во фронтире
            node = frontier.remove()
            self.num_explored += 1

            # Если целью является узел, то у нас есть решение
            if node.state == self.goal:
                actions = []
                cells = []

                # Следовать родительским узлам, чтобы найти решение
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            # Пометить узел как изученный
            self.explored.add(node.state)

            # Добавляем соседей во фронтир
            for action, state in self.neighbors(node.state):
                if not frontier.contains_stage(state) and state not in self.explored:
                    child = Node(state=state, parent=node,action=action)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        cell_size = 50
        cell_border = 2

        #Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_border),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Стены
                if col:
                    fill = (40, 40, 40)

                # Начало
                elif (i, j) == self.start:
                    fill = (0, 178, 28)

                # Цель
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Решение
                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                # Иследованное
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Пустая ячейка
                else:
                    fill = (237, 240, 252)

                # Нарисовать ячейку
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

if len(sys.argv) != 2:
    sys.exit("Usage: python maze.py maze.txt")

m = Maze(sys.argv[1])
print("Maze:")
m.print()
print("Solving...")
m.solves()
print("States Explored:", m.num_explored)
print("Solution:")
m.print()
m.output_image("maze1.png", show_explored=True)
