import time
import numpy as np
from collections import deque


class PerformanceMonitor:
    """
    Tracks real-time performance metrics for robotics control system.
    Critical for edge deployment and safety validation.
    """
    
    def __init__(self, window_size=30):
        """
        Args:
            window_size: Number of samples for rolling average
        """
        self.window_size = window_size
        
        # FPS tracking
        self.vision_fps_samples = deque(maxlen=window_size)
        self.sim_fps_samples = deque(maxlen=window_size)
        
        # Latency tracking (milliseconds)
        self.control_latency_samples = deque(maxlen=window_size)
        self.e2e_latency_samples = deque(maxlen=window_size)
        
        # Timestamps
        self.last_vision_time = time.time()
        self.last_sim_time = time.time()
        self.gesture_detect_time = None
        self.robot_response_time = None
        
    def record_vision_frame(self):
        """Call this after each hand detection"""
        current_time = time.time()
        dt = current_time - self.last_vision_time
        if dt > 0:
            fps = 1.0 / dt
            self.vision_fps_samples.append(fps)
        self.last_vision_time = current_time
        
        # Mark when gesture was detected
        self.gesture_detect_time = current_time
        
    def record_sim_step(self):
        """Call this after each physics step"""
        current_time = time.time()
        dt = current_time - self.last_sim_time
        if dt > 0:
            fps = 1.0 / dt
            self.sim_fps_samples.append(fps)
        self.last_sim_time = current_time
        
        # Calculate control latency
        if self.gesture_detect_time is not None:
            latency_ms = (current_time - self.gesture_detect_time) * 1000
            self.control_latency_samples.append(latency_ms)
            
    def get_vision_fps(self):
        """Get average vision FPS"""
        if len(self.vision_fps_samples) == 0:
            return 0.0
        return np.mean(self.vision_fps_samples)
    
    def get_sim_fps(self):
        """Get average simulation FPS"""
        if len(self.sim_fps_samples) == 0:
            return 0.0
        return np.mean(self.sim_fps_samples)
    
    def get_control_latency(self):
        """Get average control latency (ms)"""
        if len(self.control_latency_samples) == 0:
            return 0.0
        return np.mean(self.control_latency_samples)
    
    def get_latency_percentile(self, percentile=95):
        """Get latency percentile (e.g., 95th percentile)"""
        if len(self.control_latency_samples) == 0:
            return 0.0
        return np.percentile(self.control_latency_samples, percentile)
    
    def get_stats_summary(self):
        """Get complete performance summary"""
        return {
            "vision_fps": round(self.get_vision_fps(), 1),
            "sim_fps": round(self.get_sim_fps(), 1),
            "avg_latency_ms": round(self.get_control_latency(), 2),
            "p95_latency_ms": round(self.get_latency_percentile(95), 2),
            "p99_latency_ms": round(self.get_latency_percentile(99), 2),
        }
    
    def is_real_time(self, max_latency_ms=100):
        """
        Check if system is meeting real-time constraints.
        Industry standard: <100ms for human-in-the-loop control
        """
        return self.get_control_latency() < max_latency_ms
    
    def print_report(self):
        """Print performance report to console"""
        stats = self.get_stats_summary()
        real_time = "✓" if self.is_real_time() else "✗"
        
        print("\n" + "="*50)
        print("PERFORMANCE METRICS")
        print("="*50)
        print(f"Vision FPS:        {stats['vision_fps']}")
        print(f"Simulation FPS:    {stats['sim_fps']}")
        print(f"Avg Latency:       {stats['avg_latency_ms']} ms")
        print(f"95th Percentile:   {stats['p95_latency_ms']} ms")
        print(f"99th Percentile:   {stats['p99_latency_ms']} ms")
        print(f"Real-time (<100ms): {real_time}")
        print("="*50 + "\n")