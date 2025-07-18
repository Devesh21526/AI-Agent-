import time
import threading
from collections import deque
import psutil
import os

class PerformanceMonitor:
    """
    Monitor and optimize performance metrics for the voice assistant
    """

    def __init__(self, max_samples=100):
        self.max_samples = max_samples
        self.metrics = {
            'llm_response_times': deque(maxlen=max_samples),
            'speech_synthesis_times': deque(maxlen=max_samples),
            'total_response_times': deque(maxlen=max_samples),
            'memory_usage': deque(maxlen=max_samples),
            'cpu_usage': deque(maxlen=max_samples),
        }

        # Timing contexts
        self.timers = {}
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start background performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_system(self):
        """Monitor system performance metrics"""
        process = psutil.Process(os.getpid())

        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics['cpu_usage'].append(cpu_percent)

                # Memory usage
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.metrics['memory_usage'].append(memory_mb)

            except Exception as e:
                print(f"Monitoring error: {e}")

            time.sleep(1)

    def start_timer(self, name):
        """Start a timing context"""
        self.timers[name] = time.time()

    def end_timer(self, name):
        """End a timing context and record the duration"""
        if name in self.timers:
            duration = time.time() - self.timers[name]

            # Record in appropriate metric
            if name in self.metrics:
                self.metrics[name].append(duration)

            del self.timers[name]
            return duration
        return 0

    def get_stats(self):
        """Get current performance statistics"""
        stats = {}

        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values)
                }

        return stats

    def print_stats(self):
        """Print performance statistics"""
        stats = self.get_stats()

        print("\n" + "="*50)
        print("PERFORMANCE STATISTICS")
        print("="*50)

        for metric, data in stats.items():
            print(f"{metric.upper()}:")
            print(f"  Average: {data['avg']:.3f}")
            print(f"  Min: {data['min']:.3f}")
            print(f"  Max: {data['max']:.3f}")
            print(f"  Samples: {data['count']}")
            print()

    def get_recommendations(self):
        """Get performance optimization recommendations"""
        recommendations = []
        stats = self.get_stats()

        # Check LLM response times
        if 'llm_response_times' in stats:
            avg_llm_time = stats['llm_response_times']['avg']
            if avg_llm_time > 2.0:
                recommendations.append("LLM response time is slow. Consider reducing context size or using a smaller model.")

        # Check memory usage
        if 'memory_usage' in stats:
            avg_memory = stats['memory_usage']['avg']
            if avg_memory > 2000:  # 2GB
                recommendations.append("High memory usage detected. Consider clearing conversation history more frequently.")

        # Check CPU usage
        if 'cpu_usage' in stats:
            avg_cpu = stats['cpu_usage']['avg']
            if avg_cpu > 80:
                recommendations.append("High CPU usage. Consider optimizing thread count or reducing concurrent operations.")

        return recommendations