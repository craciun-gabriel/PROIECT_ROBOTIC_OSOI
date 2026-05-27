import math
import time

def navigate_path(sim, path, w_p, w_w, start_x, start_y, on_complete=None, control_flags=None):
    print("Sistemul de propulsie activat. Începe navigarea rapidă...")
    
    robot_handle = sim.getObject('/PioneerP3DX')
    left_motor = sim.getObject('/PioneerP3DX/leftMotor')
    right_motor = sim.getObject('/PioneerP3DX/rightMotor')

    def get_real_coords(gx, gy):
        def calc_c(idx):
            if idx % 2 == 0:
                return (idx // 2) * (w_p + w_w) + (w_p / 2.0)
            else:
                return (idx // 2) * (w_p + w_w) + w_p + (w_w / 2.0)
        return start_x + calc_c(gx) - (w_p / 2.0), start_y + calc_c(gy) - (w_p / 2.0)

    for node in path[1:]:
        target_x, target_y = get_real_coords(node[0], node[1])
        
        while True:
            # --- NOU: VERIFICARE STOP COMPLET ---
            if control_flags and control_flags.get("stopped", False):
                sim.setJointTargetVelocity(left_motor, 0)
                sim.setJointTargetVelocity(right_motor, 0)
                print("Misiune anulată (STOP)!")
                time.sleep(0.5)
                sim.stopSimulation()
                if on_complete:
                    on_complete(False) # Transmitem False pentru că a fost oprit
                return # Ieșim complet din funcție
            
            # --- VERIFICARE PAUZĂ ---
            if control_flags and control_flags.get("paused", False):
                sim.setJointTargetVelocity(left_motor, 0)
                sim.setJointTargetVelocity(right_motor, 0)
                time.sleep(0.1)
                continue

            pos = sim.getObjectPosition(robot_handle, sim.handle_world)
            orient = sim.getObjectOrientation(robot_handle, sim.handle_world)
            
            curr_x, curr_y = pos[0], pos[1]
            yaw = orient[2] 
            
            dx = target_x - curr_x
            dy = target_y - curr_y
            distance = math.sqrt(dx**2 + dy**2)
            target_angle = math.atan2(dy, dx)
            
            angle_error = target_angle - yaw
            angle_error = (angle_error + math.pi) % (2 * math.pi) - math.pi
            
            if distance < 0.15:
                break 
                
            v_base = 0.0 
            v_rot = 0.0  
            
            if abs(angle_error) > 0.2:
                # Se rotește pe loc mult mai agresiv
                v_rot = 5.0 * angle_error 
            else:
                # Accelerează fulgerător pe drum drept
                v_base = 10.0 * distance   
                # Corecții pe parcurs mai ferme
                v_rot = 2.5 * angle_error 
                
            # Am crescut limitele maxime de la 5.0 la 10.0 pentru înaintare
            # și de la 4.0 la 7.0 pentru viraje
            v_base = max(-10.0, min(10.0, v_base))
            v_rot = max(-7.0, min(7.0, v_rot))
            
            sim.setJointTargetVelocity(left_motor, v_base - v_rot)
            sim.setJointTargetVelocity(right_motor, v_base + v_rot)
            
            # Scădem pauza de la 0.02 la 0.01 pentru reacții de două ori mai rapide
            time.sleep(0.01)

    # Dacă a ajuns la final cu succes
    sim.setJointTargetVelocity(left_motor, 0)
    sim.setJointTargetVelocity(right_motor, 0)
    print("Misiune îndeplinită! Robotul a ajuns la destinație.")
    
    time.sleep(1.0)
    sim.stopSimulation()
    
    if on_complete:
        on_complete(True) # Transmitem True pentru succes