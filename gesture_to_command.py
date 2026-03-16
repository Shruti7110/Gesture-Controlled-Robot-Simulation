class GestureCommandMapper:
    def __init__(self):
        self.command_map = {
            'fist': {'forward': 0, 'turn': 0},      # Stop
            'open_hand': {'forward': 1, 'turn': 0}, # Move forward
            'point': {'forward': 0.5, 'turn': 0},   # Slow forward
            'peace': {'forward': 0, 'turn': 1},     # Turn right
            'thumbs_up': {'forward': -1, 'turn': 0} # Reverse
        }
    
    def get_command(self, gesture):
        """Convert gesture to robot velocity command"""
        return self.command_map.get(gesture, {'forward': 0, 'turn': 0})