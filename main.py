from sim_utils.connection import connect_to_simulator
from sim_utils.environment import build_physical_maze
from core.maze_generator import generate_maze, print_maze_to_console

# Am crescut complexitatea la 15x15. Labirintul va avea coridoare ample și o mulțime de fundături!
MAZE_WIDTH = 15
MAZE_HEIGHT = 15

def main():
    print("Se inițializează proiectul...")
    
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    print_maze_to_console(maze)
    
    client, sim = connect_to_simulator()
    
    if sim:
        print("=== CONSTRUIRE MEDIU ===")
        
        robot_handle = sim.getObject('/PioneerP3DX') #
        pos = sim.getObjectPosition(robot_handle, sim.handle_world) #
        robot_x, robot_y = pos[0], pos[1]
        
        # Nu mai trebuie să dăm cell_size, deoarece noua logică matematică știe exact cât de lat e robotul
        build_physical_maze(sim, maze, start_x=robot_x, start_y=robot_y)
        
        print("\nGata! Acum poți apăsa butonul PLAY ▶️ în CoppeliaSim.")
    else:
        print("Proiectul a fost oprit din cauza lipsei conexiunii.")

if __name__ == '__main__':
    main()