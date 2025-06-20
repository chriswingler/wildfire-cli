# Performance Monitoring Documentation

## Overview
This document outlines the performance monitoring capabilities integrated into the Wildfire Discord Bot. The system logs various metrics to help identify bottlenecks, track resource usage, and ensure efficient operation.

## Log File
- **Location**: `logs/performance_metrics.log`
- **Format**: All entries follow the standard Python logging format: `TIMESTAMP - PerformanceMetrics - LEVEL - MESSAGE`
  Example: `2023-10-27 12:00:00,123 - PerformanceMetrics - INFO - COMMAND_START: fire, User: 12345, Guild: 67890, Bot Latency: 0.1234s`

## Collected Metrics

### 1. Discord Command Performance
- **Description**: Measures Discord bot's command response times and API latency.
- **Log Signatures**:
  - `COMMAND_START: <command_name>, User: <user_id>, Guild: <guild_id_or_DM>, Bot Latency: <latency_seconds>s`
  - `COMMAND_END: <command_name>, User: <user_id>, Guild: <guild_id_or_DM>, Execution Time: <duration_seconds>s`
- **Issue Mapping**:
  - "Discord bot response time and latency monitoring"
  - "Response Time (API and command response times)"
  - "Network latency and bandwidth utilization" (Bot Latency component)

### 2. Fire Simulation Algorithm Performance
- **Description**: Tracks the execution time of core components of the fire simulation engine.
- **Log Signatures**:
  - `SIM_METHOD_START: <ClassName.method_name>`
  - `SIM_METHOD_END: <ClassName.method_name>, Execution Time: <duration_seconds>s`
- **Issue Mapping**:
  - "Fire simulation algorithm performance tracking"

### 3. System Resource Usage
- **Description**: Periodically logs CPU, memory, and garbage collection statistics.
- **Log Signatures**:
  - `RESOURCE_MONITOR: CPU Usage: <cpu_percent>%, CPU Load Avg: (<load1>, <load5>, <load15>)`
  - `RESOURCE_MONITOR: Virtual Memory: Total: ..., Available: ..., Used: ..., Percent: ...%`
  - `RESOURCE_MONITOR: Swap Memory: Total: ..., Used: ..., Percent: ...%`
  - `RESOURCE_MONITOR: Process Memory (PID: <pid>): RSS: <rss_bytes>, VMS: <vms_bytes>`
  - `RESOURCE_MONITOR: GC Counts (gen0, gen1, gen2): (<count0>, <count1>, <count2>)`
  - `RESOURCE_MONITOR: GC Thresholds: (<thresh0>, <thresh1>, <thresh2>)`
- **Issue Mapping**:
  - "Memory usage and garbage collection monitoring"
  - "Resource Usage: CPU, memory, and disk utilization trends" (Disk not explicitly logged yet)

### 4. Error Reporting
- **Description**: Enhanced error logging provides detailed context and stack traces for exceptions.
- **Log Signatures**: Standard error logs using `perf_logger.error(..., exc_info=True)` or `perf_logger.exception(...)`.
- **Issue Mapping**:
  - "Error Rates: Error frequency and type analysis" (Raw data for analysis)

### 5. Database Query Performance
- **Description**: Current setup checks for database usage.
- **Log Signature**:
  - `DATABASE_MONITORING: No active usage of 'aiosqlite' found in the current codebase. Database monitoring tasks will apply to future integrations.`
- **Issue Mapping**:
  - "Database query performance and optimization" (Currently indicates no active DB for monitoring)

## Mapping to Issue's "Performance Metrics" Section

- **Response Time (<500ms target)**: Directly measurable from `COMMAND_END` execution times.
- **Throughput (Requests per second)**: Not directly measured by current logging. Log analysis could estimate this. *Future enhancement: Implement specific throughput counter.*
- **Resource Usage (CPU, memory, disk)**: CPU and memory are logged. Disk I/O related to logging itself is not explicitly monitored.
- **Error Rates**: Errors are logged with details. Analysis of the log file is needed to calculate rates and types.
- **User Experience**: Indirectly assessed via low response times and low error rates.

## Future Enhancements
- Log rotation for `performance_metrics.log`.
- Integration with a centralized logging and analysis platform (e.g., ELK stack, Grafana Loki).
- Automated alerts for high error rates or resource usage exceeding thresholds.
- Specific metrics for throughput.
