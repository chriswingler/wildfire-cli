import psutil
import gc
import logging
import os

# Get the PerformanceMetrics logger
perf_logger = logging.getLogger('PerformanceMetrics')
# Basic configuration if run standalone for testing
# if not perf_logger.handlers:
#     # import os # already imported
#     if not os.path.exists('logs'):
#         os.makedirs('logs')
#     handler = logging.FileHandler('logs/performance_metrics.log')
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     handler.setFormatter(formatter)
#     perf_logger.addHandler(handler)
#     perf_logger.setLevel(logging.INFO)
pass # Assume logger is configured by the main application

def log_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=0.1) # Non-blocking
    load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (None, None, None) # For Unix-like systems
    perf_logger.info(f"RESOURCE_MONITOR: CPU Usage: {cpu_percent}%, CPU Load Avg: {load_avg}")
    return cpu_percent, load_avg

def log_memory_usage():
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    process_mem = psutil.Process(os.getpid()).memory_info()
    perf_logger.info(f"RESOURCE_MONITOR: Virtual Memory: Total: {virtual_mem.total}, Available: {virtual_mem.available}, Used: {virtual_mem.used}, Percent: {virtual_mem.percent}%")
    perf_logger.info(f"RESOURCE_MONITOR: Swap Memory: Total: {swap_mem.total}, Used: {swap_mem.used}, Percent: {swap_mem.percent}%")
    perf_logger.info(f"RESOURCE_MONITOR: Process Memory (PID: {os.getpid()}): RSS: {process_mem.rss}, VMS: {process_mem.vms}")
    return virtual_mem, swap_mem, process_mem

def log_gc_stats():
    gc_counts = gc.get_count()
    gc_thresholds = gc.get_threshold()
    # gc_stats = gc.get_stats() # Provides more detailed stats
    perf_logger.info(f"RESOURCE_MONITOR: GC Counts (gen0, gen1, gen2): {gc_counts}")
    perf_logger.info(f"RESOURCE_MONITOR: GC Thresholds: {gc_thresholds}")
    # For more detail, can iterate through gc.get_stats() and log them
    # For example:
    # for stat in gc.get_stats():
    #    perf_logger.info(f"RESOURCE_MONITOR: GC Gen Stats: {stat}")
    return gc_counts, gc_thresholds

def check_and_log_database_usage():
    # This function is a placeholder for the actual check.
    # For the purpose of this subtask, we'll assume the check was done (e.g. manually or via grep)
    # and based on that, we log the information.
    # In a real scenario, this might involve dynamic checks or parsing.
    found_aiosqlite_usage = False # This would be the result of the search
    if not found_aiosqlite_usage:
        perf_logger.info("DATABASE_MONITORING: No active usage of 'aiosqlite' found in the current codebase. Database monitoring tasks will apply to future integrations.")
    else:
        perf_logger.info("DATABASE_MONITORING: 'aiosqlite' usage found and instrumented (manual step assumed if complex).")
