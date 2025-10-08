from celery import current_app
from kombu import Connection
import logging

logger = logging.getLogger(__name__)


class CeleryMonitorUtils:
    """Utility class for Celery monitoring operations"""

    @staticmethod
    def get_broker_connection():
        """Get broker connection"""
        try:
            return Connection(current_app.conf.broker_url)
        except Exception as e:
            logger.error(f"Could not connect to broker: {str(e)}")
            return None

    @staticmethod
    def purge_queue(queue_name='erp_master_queue'):
        """Purge all messages from a queue"""
        try:
            current_app.control.purge()
            return True
        except Exception as e:
            logger.error(f"Error purging queue {queue_name}: {str(e)}")
            return False

    @staticmethod
    def get_task_info_by_name(task_name):
        """Get all tasks with specific name"""
        try:
            inspect = current_app.control.inspect()

            all_tasks = []

            # Check active tasks
            active = inspect.active() or {}
            for worker, tasks in active.items():
                for task in tasks:
                    if task.get('name') == task_name:
                        task['worker'] = worker
                        task['status'] = 'active'
                        all_tasks.append(task)

            # Check scheduled tasks
            scheduled = inspect.scheduled() or {}
            for worker, tasks in scheduled.items():
                for task in tasks:
                    if task.get('name') == task_name:
                        task['worker'] = worker
                        task['status'] = 'scheduled'
                        all_tasks.append(task)

            # Check reserved tasks
            reserved = inspect.reserved() or {}
            for worker, tasks in reserved.items():
                for task in tasks:
                    if task.get('name') == task_name:
                        task['worker'] = worker
                        task['status'] = 'reserved'
                        all_tasks.append(task)

            return all_tasks

        except Exception as e:
            logger.error(f"Error getting tasks for {task_name}: {str(e)}")
            return []

    @staticmethod
    def broadcast_task_control(action, **kwargs):
        """Broadcast control commands to all workers"""
        try:
            control = current_app.control

            if action == 'shutdown':
                control.shutdown(**kwargs)
            elif action == 'pool_restart':
                control.pool_restart(**kwargs)
            elif action == 'pool_grow':
                control.pool_grow(n=kwargs.get('n', 1), **kwargs)
            elif action == 'pool_shrink':
                control.pool_shrink(n=kwargs.get('n', 1), **kwargs)
            elif action == 'add_consumer':
                control.add_consumer(
                    queue=kwargs.get('queue', 'erp_master_queue'),
                    **kwargs
                )
            elif action == 'cancel_consumer':
                control.cancel_consumer(
                    queue=kwargs.get('queue', 'erp_master_queue'),
                    **kwargs
                )
            else:
                return False, f"Unknown action: {action}"

            return True, f"Successfully executed {action}"

        except Exception as e:
            logger.error(f"Error executing {action}: {str(e)}")
            return False, str(e)


from typing import Dict, Any, List


class CeleryStatsParser:
    """Utility class to safely parse Celery worker stats"""

    @staticmethod
    def safe_get_dict(data: Any, default: Dict = None) -> Dict:
        """Safely get dictionary from potentially non-dict data"""
        if default is None:
            default = {}
        return data if isinstance(data, dict) else default

    @staticmethod
    def safe_get_number(data: Any, default: int = 0) -> int:
        """Safely convert data to number"""
        if data is None:
            return default
        try:
            return int(data)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_get_float(data: Any, default: float = 0.0) -> float:
        """Safely convert data to float"""
        if data is None:
            return default
        try:
            return float(data)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def parse_worker_rusage(rusage: Any) -> Dict[str, int]:
        """Parse worker rusage information safely"""
        rusage_dict = CeleryStatsParser.safe_get_dict(rusage)

        return {
            'memory_usage': CeleryStatsParser.safe_get_number(rusage_dict.get('maxrss', 0)),
            'user_time': CeleryStatsParser.safe_get_float(rusage_dict.get('utime', 0.0)),
            'system_time': CeleryStatsParser.safe_get_float(rusage_dict.get('stime', 0.0)),
            'voluntary_context_switches': CeleryStatsParser.safe_get_number(rusage_dict.get('nvcsw', 0)),
            'involuntary_context_switches': CeleryStatsParser.safe_get_number(rusage_dict.get('nivcsw', 0)),
        }

    @staticmethod
    def parse_worker_pool(pool: Any) -> Dict[str, Any]:
        """Parse worker pool information safely"""
        pool_dict = CeleryStatsParser.safe_get_dict(pool)

        return {
            'implementation': pool_dict.get('implementation', 'unknown'),
            'max_concurrency': CeleryStatsParser.safe_get_number(pool_dict.get('max-concurrency', 0)),
            'processes': CeleryStatsParser.safe_get_number(pool_dict.get('processes', [])),
        }

    @staticmethod
    def calculate_load_avg(active_tasks: int, max_concurrency: int) -> float:
        """Calculate load average as percentage"""
        if max_concurrency <= 0:
            return 0.0
        return min(active_tasks / max_concurrency, 1.0)

    @staticmethod
    def parse_worker_stats(worker_name: str, stats: Any, active_tasks: List) -> Dict[str, Any]:
        """Comprehensive worker stats parsing"""
        if not isinstance(stats, dict):
            logger.warning(f"Worker {worker_name} returned non-dict stats: {type(stats)}")
            return {
                'name': worker_name,
                'status': 'unreachable',
                'active_tasks': len(active_tasks),
                'load_avg': 0.0,
                'memory_usage': 0,
                'max_concurrency': 0,
                'pool_type': 'unknown',
                'total_tasks': {},
                'clock': 0,
                'user_time': 0.0,
                'system_time': 0.0,
                'error': 'Worker returned invalid stats format'
            }

        try:
            # Parse rusage information
            rusage_info = CeleryStatsParser.parse_worker_rusage(stats.get('rusage'))

            # Parse pool information
            pool_info = CeleryStatsParser.parse_worker_pool(stats.get('pool'))

            # Calculate load
            active_task_count = len(active_tasks)
            load_avg = CeleryStatsParser.calculate_load_avg(
                active_task_count,
                pool_info['max_concurrency']
            )

            # Parse total tasks
            total_tasks = CeleryStatsParser.safe_get_dict(stats.get('total'))

            return {
                'name': worker_name,
                'status': 'online',
                'active_tasks': active_task_count,
                'load_avg': load_avg,
                'memory_usage': rusage_info['memory_usage'],
                'max_concurrency': pool_info['max_concurrency'],
                'pool_type': pool_info['implementation'],
                'total_tasks': total_tasks,
                'clock': CeleryStatsParser.safe_get_number(stats.get('clock')),
                'user_time': rusage_info['user_time'],
                'system_time': rusage_info['system_time'],
                'processes_count': len(pool_info['processes']) if isinstance(pool_info['processes'], list) else
                pool_info['processes'],
            }

        except Exception as e:
            logger.error(f"Error parsing stats for worker {worker_name}: {str(e)}")
            return {
                'name': worker_name,
                'status': 'error',
                'active_tasks': len(active_tasks),
                'load_avg': 0.0,
                'memory_usage': 0,
                'max_concurrency': 0,
                'pool_type': 'unknown',
                'total_tasks': {},
                'clock': 0,
                'user_time': 0.0,
                'system_time': 0.0,
                'error': str(e)
            }
