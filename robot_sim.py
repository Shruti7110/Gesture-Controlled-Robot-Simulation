import pybullet as p
import pybullet_data
import time
import random
import math


class SimpleRobotSim:
    def __init__(self):
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

        p.setGravity(0, 0, -10)

        # -------- FLOOR --------
        self.plane_id = p.loadURDF("plane.urdf")

        # Try yellow checker → fallback to blue
        texture_id = p.loadTexture("warehouse.png")

        p.changeVisualShape(self.plane_id, -1, textureUniqueId=texture_id)

        # Light overlay color (fresh warehouse feel)
        p.changeVisualShape(self.plane_id, -1, rgbaColor=[0.9, 0.9, 0.9, 1])

        # Grid lines (for spatial clarity)
        grid_size = 8
        for i in range(-grid_size, grid_size + 1):
            p.addUserDebugLine([i, -grid_size, 0.01], [i, grid_size, 0.01], [0.7, 0.7, 0.7], 1)
            p.addUserDebugLine([-grid_size, i, 0.01], [grid_size, i, 0.01], [0.7, 0.7, 0.7], 1)

        # -------- PARCEL --------
        collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.3, 0.15])
        visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[0.3, 0.3, 0.15],
            rgbaColor=[0.65, 0.45, 0.25, 1],
        )

        self.robot_id = p.createMultiBody(
            baseMass=10,
            baseCollisionShapeIndex=collision,
            baseVisualShapeIndex=visual,
            basePosition=[0, 0, 0.15],
        )

        # -------- FRONT MARKER --------
        marker_visual = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[0.1, 0.02, 0.02],
            rgbaColor=[0, 0, 0, 1],
        )

        self.front_marker = p.createMultiBody(
            baseMass=0,
            baseVisualShapeIndex=marker_visual,
            basePosition=[0, 0, 0],
        )

        # Camera
        p.resetDebugVisualizerCamera(
            cameraDistance=5,
            cameraYaw=0,
            cameraPitch=-89,
            cameraTargetPosition=[0, 0, 0],
        )
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1)

        # Motion tuning (FIXED TURNING)
        self.velocity = [0, 0]
        self.max_speed = 3.0
        self.max_turn = 2.5

        # Game state
        self.battery = 7
        self.max_battery = 7
        self.collisions = 0
        self.game_active = True
        self.game_won = False
        self.start_time = time.time()
        self.time_limit = 80

        self.obstacles = []
        self.goal_position = [3.0, 3.0, 0.1]
        self.goal_markers = []
        
        # ✅ ADDED: Collision tracking
        self.collision_cooldown = {}
        self.cooldown_duration = 1.0

        self._setup_warehouse()

    # -------------------------------
    def _setup_warehouse(self):
        num_obstacles = random.randint(6, 10)

        goal_x = random.uniform(2, 3.5)
        goal_y = random.uniform(2, 3.5)
        self.goal_position = [goal_x, goal_y, 0.1]

        # -------- GOAL (PRECISION) --------
        goal_size = 0.4
        goal_floor = p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[goal_size, goal_size, 0.01],
            rgbaColor=[0.2, 0.9, 0.3, 0.6],
        )

        self.goal_markers.append(
            p.createMultiBody(
                baseMass=0,
                baseVisualShapeIndex=goal_floor,
                basePosition=[goal_x, goal_y, 0.02],
            )
        )

        # -------- OBSTACLES --------
        placed_obstacles = 0
        max_attempts = 100  # Prevent infinite loop
        
        while placed_obstacles < num_obstacles and max_attempts > 0:
            max_attempts -= 1
            
            # Random position
            x = random.uniform(-3, 3)
            y = random.uniform(-3, 3)
            
            # ✅ CHECK 1: Not too close to robot start (0, 0)
            dist_to_start = math.sqrt(x**2 + y**2)
            if dist_to_start < 1.5:  # Keep 1.5m clear around start
                continue
            
            # ✅ CHECK 2: Not too close to goal
            dist_to_goal = math.sqrt((x - goal_x)**2 + (y - goal_y)**2)
            if dist_to_goal < 1.2:  # Keep 1.2m clear around goal
                continue
            
            # ✅ CHECK 3: Not too close to other obstacles
            too_close = False
            for other_box in self.obstacles:
                other_pos, _ = p.getBasePositionAndOrientation(other_box)
                dist = math.sqrt((x - other_pos[0])**2 + (y - other_pos[1])**2)
                if dist < 1.0:  # Keep 1m spacing between obstacles
                    too_close = True
                    break
            
            if too_close:
                continue
            
            # ✅ All checks passed - place obstacle
            size = random.choice([0.5, 0.7, 1.0])
            half = size / 2

            col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[half, half, half])
            vis = p.createVisualShape(
                p.GEOM_BOX,
                halfExtents=[half, half, half],
                rgbaColor=[0.3, 0.3, 0.35, 1],
            )

            box = p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=col,
                baseVisualShapeIndex=vis,
                basePosition=[x, y, half],
            )

            self.obstacles.append(box)
            self.collision_cooldown[box] = 0
            placed_obstacles += 1

    # -------------------------------
    def update_velocity(self, forward, turn):
        if self.game_active:
            forward = max(-1, min(1, forward))
            turn = max(-1, min(1, turn))
            self.velocity = [forward, turn]

    # -------------------------------
    def step(self):
        if not self.game_active:
            return
        
        # ✅ ADDED: Check time limit
        if time.time() - self.start_time > self.time_limit:
            self.game_active = False
            print("⏰ TIME'S UP - MISSION FAILED")
            return

        forward, turn = self.velocity

        pos, orn = p.getBasePositionAndOrientation(self.robot_id)
        yaw = p.getEulerFromQuaternion(orn)[2]

        # -------- BETTER TURNING --------
        turn_gain = 1.5
        rotation_damping = 0.6   # Reduce spin in place speed for better control
        omega = turn * self.max_turn * turn_gain

        if abs(turn) < 0.05:
            omega *= rotation_damping
            
        # if abs(forward) < 0.1:
        #     omega *= 1.8  # spin in place boost

        turn_penalty = 1 - min(abs(turn), 1) * 0.6  # Reduce forward speed when turning sharply

        vx = forward * self.max_speed * turn_penalty * math.cos(yaw)
        vy = forward * self.max_speed * turn_penalty * math.sin(yaw)

        p.resetBaseVelocity(
            self.robot_id,
            linearVelocity=[vx, vy, 0],
            angularVelocity=[0, 0, omega],
        )

        # -------- FRONT MARKER UPDATE --------
        offset = 0.35
        mx = pos[0] + offset * math.cos(yaw)
        my = pos[1] + offset * math.sin(yaw)

        p.resetBasePositionAndOrientation(
            self.front_marker,
            [mx, my, pos[2] + 0.2],
            orn,
        )

        p.stepSimulation()

        # ✅ ADDED: Check collisions
        self.check_collisions()
        
        self.check_goal_reached()

    # ✅ ADDED: Collision detection with battery drain
    def check_collisions(self):
        current_time = time.time()
        for obstacle in self.obstacles:
            # Check cooldown
            if current_time - self.collision_cooldown[obstacle] < self.cooldown_duration:
                continue

            # Check for collision
            if p.getContactPoints(self.robot_id, obstacle):
                self.battery -= 1
                self.collisions += 1
                self.collision_cooldown[obstacle] = current_time

                print(f"💥 Collision! Battery: {self.battery}/{self.max_battery}")

                # Game over if battery depleted
                if self.battery <= 0:
                    self.game_active = False
                    print("🔋 BATTERY DEPLETED - GAME OVER")

    # -------------------------------
    def check_goal_reached(self):
        pos, _ = p.getBasePositionAndOrientation(self.robot_id)
        dx = pos[0] - self.goal_position[0]
        dy = pos[1] - self.goal_position[1]

        if abs(dx) < 0.35 and abs(dy) < 0.35:
            self.game_active = False
            self.game_won = True
            print("📦 ✅ DELIVERY COMPLETE!")

    # -------------------------------
    def get_game_state(self):
        return {
            "battery": self.battery,
            "max_battery": self.max_battery,
            "collisions": self.collisions,
            "elapsed_time": time.time() - self.start_time,
            "time_limit": self.time_limit,
            "game_active": self.game_active,
            "game_won": self.game_won,
            "score": 0,
        }

    def close(self):
        p.disconnect()