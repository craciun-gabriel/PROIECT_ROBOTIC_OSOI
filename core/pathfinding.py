from collections import deque

def find_path_lee(maze, start_coord, goal_coord):
    """
    Găsește cel mai scurt drum într-un labirint folosind Algoritmul lui Lee (BFS).
    
    :param maze: Matricea 2D a labirintului (0 = drum, 1 = perete)
    :param start_coord: Tuplu (x, y) pentru poziția de start
    :param goal_coord: Tuplu (x, y) pentru destinație
    :return: O listă de tupluri [(x,y), ...] reprezentând calea, sau None dacă nu există drum.
    """
    rows = len(maze)
    cols = len(maze[0])
    
    # Coada va stoca tupluri de forma: (pozitie_curenta, calea_pana_aici)
    queue = deque([(start_coord, [start_coord])])
    
    # Set pentru a ține minte pe unde am fost deja (ca să nu ne învârtim în cerc)
    visited = set()
    visited.add(start_coord)
    
    # Direcțiile posibile: Dreapta, Jos, Stânga, Sus
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    
    while queue:
        (curr_x, curr_y), path = queue.popleft()
        
        # Dacă am ajuns la destinație, returnăm drumul!
        if (curr_x, curr_y) == goal_coord:
            return path
            
        # Explorăm vecinii
        for dx, dy in directions:
            nx, ny = curr_x + dx, curr_y + dy
            
            # Verificăm dacă vecinul este în limitele matricii
            if 0 <= nx < cols and 0 <= ny < rows:
                # Verificăm dacă este drum (0) și nu am mai fost pe acolo
                if maze[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    # Adăugăm noua poziție în coadă, împreună cu istoricul pașilor
                    queue.append(((nx, ny), path + [(nx, ny)]))
                    
    # Dacă coada s-a golit și nu am găsit destinația
    return None

def print_path_on_maze(maze, path):
    """Afișează matricea în consolă, desenând traseul găsit cu ' * '."""
    print("\n--- Traseul Găsit (Algoritmul Lee) ---")
    for y in range(len(maze)):
        row_str = ""
        for x in range(len(maze[0])):
            if (x, y) in path:
                row_str += " * " # Acesta este drumul robotului
            elif maze[y][x] == 1:
                row_str += "███" # Perete
            else:
                row_str += "   " # Drum liber neexplorat
        print(row_str)
    print("--------------------------------------\n")