class HandJoystick:
    """
    Hand gesture joystick controller for warehouse robot.
    Maps hand position to robot movement commands.
    Only recognizes 4 directions: UP, DOWN, LEFT, RIGHT
    """

    def __init__(self):
        # Control sensitivity (increased for more responsiveness)
        self.forward_sensitivity = 3.0  # Increased from 2.0
        self.turn_sensitivity = 3.0      # Increased from 2.0
        
        # Deadzone to prevent drift (reduced for more sensitivity)
        self.deadzone = 0.05  # Reduced from 0.15
        
        # Direction threshold - hand must be clearly in one direction
        self.direction_threshold = 0.2

    def get_command(self, landmarks):
        """
        Convert hand landmarks to robot control commands.
        Only allows pure UP/DOWN (forward/backward) or LEFT/RIGHT (turning).
        
        Args:
            landmarks: MediaPipe hand landmarks (21 points)
            
        Returns:
            tuple: (forward, turn) values in range [-1, 1]
        """
        
        # Use landmark 9 (middle finger base) as control point
        x = landmarks[9].x
        y = landmarks[9].y

        # Screen center (normalized coordinates)
        cx = 0.5
        cy = 0.5

        # Calculate offset from center
        dx = x - cx
        dy = y - cy

        # Start with no movement
        forward = 0
        turn = 0

        # Calculate absolute distances
        abs_dx = abs(dx)
        abs_dy = abs(dy)

        # Check if hand is outside deadzone
        if abs_dx < self.deadzone and abs_dy < self.deadzone:
            # Hand is in center deadzone - no movement
            return 0, 0

        # Determine primary direction (vertical or horizontal)
        # Only allow one direction at a time
        if abs_dy > abs_dx:
            # Vertical movement is dominant (UP or DOWN)
            if abs_dy > self.direction_threshold:
                # Map Y-axis to forward/backward
                forward = -dy * self.forward_sensitivity
                forward = max(min(forward, 1), -1)
                turn = 0  # No turning when moving forward/backward
        else:
            # Horizontal movement is dominant (LEFT or RIGHT)
            if abs_dx > self.direction_threshold:
                # Map X-axis to turning
                turn = dx * self.turn_sensitivity
                turn = max(min(turn, 1), -1)
                forward = 0  # No forward when turning

        return forward, turn
    
    def get_direction_name(self, landmarks):
        """
        Get the name of the current direction for display.
        
        Returns:
            str: "UP", "DOWN", "LEFT", "RIGHT", or "CENTER"
        """
        forward, turn = self.get_command(landmarks)
        
        if abs(forward) < 0.1 and abs(turn) < 0.1:
            return "CENTER"
        elif forward > 0.1:
            return "UP (Forward)"
        elif forward < -0.1:
            return "DOWN (Backward)"
        elif turn > 0.1:
            return "RIGHT (Turn Right)"
        elif turn < -0.1:
            return "LEFT (Turn Left)"
        else:
            return "CENTER"
    
    def get_distance_from_center(self, landmarks):
        """
        Calculate how far the hand is from the center of control zone.
        Useful for UI feedback.
        
        Returns:
            float: Distance from center (0 to ~0.7)
        """
        x = landmarks[9].x
        y = landmarks[9].y
        cx = 0.5
        cy = 0.5
        
        import math
        distance = math.sqrt((x - cx)**2 + (y - cy)**2)
        return distance
    
    def is_hand_in_control_zone(self, landmarks, zone_radius=0.3):
        """
        Check if hand is within the control circle.
        
        Args:
            landmarks: MediaPipe hand landmarks
            zone_radius: Radius of control zone (normalized)
            
        Returns:
            bool: True if hand is in control zone
        """
        distance = self.get_distance_from_center(landmarks)
        return distance <= zone_radius