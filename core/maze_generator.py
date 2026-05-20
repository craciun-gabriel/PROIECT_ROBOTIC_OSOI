import random

def generate_maze(width, height, obstacle_density=None):
    """
    Generează un labirint clasic folosind algoritmul Recursive Backtracker (DFS).
    Creează culoare continue și pereți perfect uniți.
    (Parametrul obstacle_density este păstrat doar ca să nu dea eroare în main.py, dar nu mai e folosit).
    """
    # Pentru acest algoritm clasic, dimensiunile trebuie să fie impare
    if width % 2 == 0: width += 1
    if height % 2 == 0: height += 1

    # Inițializăm labirintul ca fiind 100% pereți (1)
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_passages(cx, cy):
        # Direcțiile: Sus, Jos, Stânga, Dreapta (sărim peste o celulă pentru a lăsa perete)
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy

            # Dacă următoarea celulă e în grid și este încă perete
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                # Spargem peretele dintre noi și celula destinație
                maze[cy + dy//2][cx + dx//2] = 0
                # Spargem și celula destinație
                maze[ny][nx] = 0
                # Mergem mai departe din acea celulă
                carve_passages(nx, ny)

    # Pornim spargerea culoarelor de la coordonata (0,0) - Start
    maze[0][0] = 0
    carve_passages(0, 0)

    # Asigurăm o ieșire validă în colțul din dreapta-jos - Sosire
    maze[height-1][width-1] = 0
    # Ne asigurăm că ieșirea se conectează la restul labirintului
    if maze[height-2][width-1] == 1 and maze[height-1][width-2] == 1:
        maze[height-2][width-1] = 0

    return maze

def print_maze_to_console(maze):
    """Afișează matricea frumos în consolă, folosind blocuri duble pentru aspect de perete."""
    print("\n--- Harta Labirintului ---")
    for row in maze:
        row_str = "".join(["██" if cell == 1 else "  " for cell in row])
        print(row_str)
    print("--------------------------\n")