import pybullet as p
import pybullet_data
import time

class SimpleRobotSim:
    def __init__(self):
        # Start PyBullet in GUI mode
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # Set up environment
        p.setGravity(0, 0, -10)
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Load a simple robot (we'll use a car for now)
        self.robot_id = p.loadURDF("husky/husky.urdf", [0, 0, 0.5])
        self.wheels = [2, 3, 4, 5]  # Husky wheel joints
        
        # Camera setup
        p.resetDebugVisualizerCamera(
            cameraDistance=3,
            cameraYaw=45,
            cameraPitch=-30,
            cameraTargetPosition=[0, 0, 0]
        )
        
        self.velocity = [0, 0]  # [forward/backward, left/right]
    
    def update_velocity(self, forward, turn):
        """Update robot movement based on gesture commands"""
        self.velocity = [forward, turn]
    
    def step(self):
        """Advance simulation by one step"""

        forward, turn = self.velocity

        left_speed = forward - turn
        right_speed = forward + turn

        wheel_speeds = [
            left_speed,   # front left
            right_speed,  # front right
            left_speed,   # rear left
            right_speed   # rear right
        ]

        for wheel, speed in zip(self.wheels, wheel_speeds):

            p.setJointMotorControl2(
                self.robot_id,
                wheel,
                p.VELOCITY_CONTROL,
                targetVelocity=speed * 15,
                force=100
            )

        p.stepSimulation()
        
    def close(self):
        p.disconnect()

# Test the simulation
if __name__ == "__main__":
    sim = SimpleRobotSim()
    
    for i in range(10000):
        sim.step()
    
    sim.close()