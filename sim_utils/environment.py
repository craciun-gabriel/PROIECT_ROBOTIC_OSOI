def build_physical_maze(sim, maze, start_x=0.0, start_y=0.0):
    """
    Construiește un labirint profesional cu pereți subțiri și culoare largi.
    """
    print("Se construiesc pereții 3D și marginile arenei...")
    wall_height = 0.4
    
    # --- PARAMETRI CHEIE ---
    w_p = 0.65  # Lățimea drumului (pe unde merge robotul)
    w_w = 0.1   # Grosimea peretelui (foarte subțire)
    overlap = 0.02 # O mică suprapunere pentru ca pereții să se îmbine perfect la colțuri
    
    def get_coord_and_size(idx):
        """Calculează poziția și dimensiunea fizică în funcție de tipul celulei (drum sau perete)."""
        if idx % 2 == 0:
            # Este o celulă de drum (indecși pari)
            pos = (idx // 2) * (w_p + w_w) + (w_p / 2.0)
            return pos, w_p
        else:
            # Este o celulă de perete (indecși impari)
            pos = (idx // 2) * (w_p + w_w) + w_p + (w_w / 2.0)
            return pos, w_w

    # --- 1. CONSTRUIREA OBSTACOLELOR INTERIOARE ---
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                cx, sx = get_coord_and_size(x)
                cy, sy = get_coord_and_size(y)
                
                # Creăm blocul 3D
                sizes = [sx + overlap, sy + overlap, wall_height]
                wall_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, sizes, 0)
                
                if wall_handle != -1:
                    # Aliniem labirintul astfel încât robotul să fie fix în centrul primei celule (0,0)
                    pos_x = start_x + cx - (w_p / 2.0)
                    pos_y = start_y + cy - (w_p / 2.0)
                    pos_z = wall_height / 2.0 
                    
                    sim.setObjectPosition(wall_handle, sim.handle_world, [pos_x, pos_y, pos_z]) #
                    sim.setObjectInt32Param(wall_handle, 3003, 1)

    # --- 2. CONSTRUIREA BORDURILOR EXTERIOARE ---
    rows, cols = len(maze), len(maze[0])
    total_x = (cols // 2 + 1) * w_p + (cols // 2) * w_w
    total_y = (rows // 2 + 1) * w_p + (rows // 2) * w_w
    
    center_x = start_x + total_x / 2.0 - w_p / 2.0
    center_y = start_y + total_y / 2.0 - w_p / 2.0
    b_thick = 0.1 # Grosimea bordurii
    
    borders = [
        ([total_x + b_thick*2, b_thick, wall_height], [center_x, start_y - w_p/2 - b_thick/2, wall_height/2]), # Sus
        ([total_x + b_thick*2, b_thick, wall_height], [center_x, start_y + total_y - w_p/2 + b_thick/2, wall_height/2]), # Jos
        ([b_thick, total_y, wall_height], [start_x - w_p/2 - b_thick/2, center_y, wall_height/2]), # Stânga
        ([b_thick, total_y, wall_height], [start_x + total_x - w_p/2 + b_thick/2, center_y, wall_height/2]) # Dreapta
    ]
    
    for size, pos in borders:
        b_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, size, 0)
        if b_handle != -1:
            sim.setObjectPosition(b_handle, sim.handle_world, pos) #
            sim.setObjectInt32Param(b_handle, 3003, 1)
            
    print("Construcția labirintului a fost finalizată cu succes!")