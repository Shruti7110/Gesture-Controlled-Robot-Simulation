import csv
import time
from datetime import datetime


class PerformanceLogger:
    """
    Logs performance metrics to CSV for post-game analysis.
    Essential for optimization and benchmarking.
    """
    
    def __init__(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_log_{timestamp}.csv"
        
        self.filename = filename
        self.log_file = open(filename, 'w', newline='')
        self.writer = csv.writer(self.log_file)
        
        # Write header
        self.writer.writerow([
            'timestamp',
            'vision_fps',
            'sim_fps',
            'control_latency_ms',
            'battery',
            'collisions',
            'game_active'
        ])
        
    def log(self, perf_monitor, game_state):
        """Log current frame data"""
        stats = perf_monitor.get_stats_summary()
        
        self.writer.writerow([
            time.time(),
            stats['vision_fps'],
            stats['sim_fps'],
            stats['avg_latency_ms'],
            game_state['battery'],
            game_state['collisions'],
            game_state['game_active']
        ])
        
    def close(self):
        """Close log file"""
        self.log_file.close()
        print(f"Performance log saved to: {self.filename}")