class HandJoystick:

    def get_command(self, landmarks):

        x = landmarks[9].x
        y = landmarks[9].y

        # center of screen
        cx = 0.5
        cy = 0.5

        dx = x - cx
        dy = y - cy

        forward = -dy * 2
        turn = dx * 2

        # clamp values
        forward = max(min(forward, 1), -1)
        turn = max(min(turn, 1), -1)

        return forward, turn