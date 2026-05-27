import random

def generate_maze(width, height):
    """Generează labirintul DFS și alege o destinație aleatorie."""
    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1

    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_passages(cx, cy):
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[cy + dy//2][cx + dx//2] = 0
                maze[ny][nx] = 0
                carve_passages(nx, ny)

    maze[0][0] = 0
    carve_passages(0, 0)

    # --- NOU: Găsim o destinație aleatorie ---
    empty_cells = []
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 0 and (x, y) != (0, 0):
                empty_cells.append((x, y))

    # Sortăm celulele după distanță față de start și alegem random din cele mai îndepărtate
    empty_cells.sort(key=lambda c: c[0] + c[1], reverse=True)
    top_farthest = empty_cells[:max(1, len(empty_cells)//4)]
    goal_pos = random.choice(top_farthest)

    return maze, goal_pos

def print_maze_to_console(maze):
    print("\n--- Harta Labirintului ---")
    for row in maze:
        row_str = "".join(["██" if cell == 1 else "  " for cell in row])
        print(row_str)
    print("--------------------------\n")