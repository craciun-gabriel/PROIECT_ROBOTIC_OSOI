def build_physical_maze(sim, maze, robot_handle, goal_pos, path_width=0.65, wall_thickness=0.1, wall_height=0.4):
    """Construiește mediul fizic cu MĂȘTI DE COLIZIUNE explicite pentru a susține robotul."""
    print("Se construiește mediul 3D...")
    
    w_p = path_width
    w_w = wall_thickness
    overlap = 0.02 
    
    handles_created = []
    rows, cols = len(maze), len(maze[0])
    
    total_x = (cols // 2 + 1) * w_p + (cols // 2) * w_w
    total_y = (rows // 2 + 1) * w_p + (rows // 2) * w_w
    
    start_x = -total_x / 2.0 + w_p / 2.0
    start_y = -total_y / 2.0 + w_p / 2.0
    
    # Lăsăm robotul să cadă de la 30 cm
    sim.setObjectPosition(robot_handle, sim.handle_world, [start_x, start_y, 0.3]) 
    
    floor_thickness = 0.05
    
    # --- 1. PODEAUA (Beton armat digital) ---
    floor_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [total_x + 0.2, total_y + 0.2, floor_thickness], 0)
    if floor_handle != -1:
        sim.setObjectPosition(floor_handle, sim.handle_world, [0, 0, floor_thickness / 2.0]) 
        
        sim.setObjectInt32Param(floor_handle, 3003, 1) # 3003 = Statică (ca să nu cadă și ea cu totul)
        sim.setObjectInt32Param(floor_handle, 3004, 1) # 3004 = Respondable (obiect cu masă fizică)
        sim.setObjectInt32Param(floor_handle, 3019, 65535) # 3019 = Mască Coliziune (se lovește de TOATE obiectele)
        
        sim.setShapeColor(floor_handle, None, sim.colorcomponent_ambient_diffuse, [0.3, 0.3, 0.3])
        handles_created.append(floor_handle)

    def get_coord_and_size(idx):
        if idx % 2 == 0:
            return (idx // 2) * (w_p + w_w) + (w_p / 2.0), w_p
        else:
            return (idx // 2) * (w_p + w_w) + w_p + (w_w / 2.0), w_w

    # --- 2. OBSTACOLE INTERIOARE ---
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                cx, sx = get_coord_and_size(x)
                cy, sy = get_coord_and_size(y)
                
                sizes = [sx + overlap, sy + overlap, wall_height]
                wall_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, sizes, 0)
                
                if wall_handle != -1:
                    pos_x = start_x + cx - (w_p / 2.0)
                    pos_y = start_y + cy - (w_p / 2.0)
                    pos_z = floor_thickness + wall_height / 2.0 
                    sim.setObjectPosition(wall_handle, sim.handle_world, [pos_x, pos_y, pos_z]) 
                    
                    sim.setObjectInt32Param(wall_handle, 3003, 1)
                    sim.setObjectInt32Param(wall_handle, 3004, 1)
                    sim.setObjectInt32Param(wall_handle, 3019, 65535) # Coliziune activată și la pereți
                    
                    handles_created.append(wall_handle)

    # --- 3. BORDURI EXTERIOARE ---
    b_thick = 0.1 
    borders = [
        ([total_x + b_thick*2, b_thick, wall_height], [0, -total_y/2 - b_thick/2, floor_thickness + wall_height/2]),
        ([total_x + b_thick*2, b_thick, wall_height], [0, total_y/2 + b_thick/2, floor_thickness + wall_height/2]),
        ([b_thick, total_y, wall_height], [-total_x/2 - b_thick/2, 0, floor_thickness + wall_height/2]),
        ([b_thick, total_y, wall_height], [total_x/2 + b_thick/2, 0, floor_thickness + wall_height/2])
    ]
    for size, pos in borders:
        b_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, size, 0)
        if b_handle != -1:
            sim.setObjectPosition(b_handle, sim.handle_world, pos) 
            sim.setObjectInt32Param(b_handle, 3003, 1)
            sim.setObjectInt32Param(b_handle, 3004, 1)
            sim.setObjectInt32Param(b_handle, 3019, 65535) # Coliziune activată
            handles_created.append(b_handle)

    # --- 4. MARKER DESTINAȚIE (Asta rămâne Hologramă!) ---
    gx, gy = goal_pos
    cx, _ = get_coord_and_size(gx)
    cy, _ = get_coord_and_size(gy)
    dest_x = start_x + cx - (w_p / 2.0)
    dest_y = start_y + cy - (w_p / 2.0)
    
    # Parametrul de coliziune LIPSĂ intenționat, ca robotul să poată călca pe el!
    dest_handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, [w_p, w_p, 0.02], 0)
    if dest_handle != -1:
        sim.setObjectPosition(dest_handle, sim.handle_world, [dest_x, dest_y, floor_thickness + 0.01]) 
        sim.setObjectInt32Param(dest_handle, 3003, 1) 
        sim.setShapeColor(dest_handle, None, sim.colorcomponent_ambient_diffuse, [0.1, 0.9, 0.1]) 
        handles_created.append(dest_handle)

    return handles_created