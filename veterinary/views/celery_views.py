from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from celery import current_app
from celery.result import AsyncResult
import json
from typing import Dict
import logging

from facilitator.authentication import ApiKeyAuthentication
from veterinary.utils.celery_util import CeleryMonitorUtils, CeleryStatsParser

logger = logging.getLogger(__name__)


class CeleryTaskMonitorMixin:
    """Mixin class for common Celery monitoring functionality"""

    def get_celery_inspect(self):
        """Get Celery inspect instance"""
        return current_app.control.inspect()

    def format_task_info(self, task_data: Dict) -> Dict:
        """Format task information for API response"""
        return {
            'task_id': task_data.get('id', ''),
            'name': task_data.get('name', ''),
            'state': task_data.get('state', 'UNKNOWN'),
            'received': task_data.get('received', None),
            'started': task_data.get('started', None),
            'timestamp': task_data.get('timestamp', None),
            'runtime': task_data.get('runtime', None),
            'result': task_data.get('result', None),
            'exception': task_data.get('exception', None),
            'traceback': task_data.get('traceback', None),
            'args': task_data.get('args', []),
            'kwargs': task_data.get('kwargs', {}),
            'eta': task_data.get('eta', None),
            'expires': task_data.get('expires', None),
            'retries': task_data.get('retries', 0),
            'worker': task_data.get('worker', ''),
            'queue': task_data.get('queue', 'celery'),
        }


from erp_master.celery import celery_app


class TasksAPIView(APIView):
    """API to get tasks filtered by state"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        state_filter = request.query_params.get("state")  # e.g. ACTIVE, SUCCESS, FAILURE
        task_ids = request.query_params.getlist("task_ids")  # optional filter by task_id

        tasks = []

        try:
            # 1️⃣ Inspect active tasks (running)
            inspect = celery_app.control.inspect()
            active_tasks = inspect.active() or {}
            for worker, worker_tasks in active_tasks.items():
                for task in worker_tasks:
                    task_info = {
                        "task_id": task.get("id"),
                        "name": task.get("name"),
                        "state": "ACTIVE",
                        "args": task.get("args"),
                        "kwargs": task.get("kwargs"),
                        "worker": worker,
                        "time_start": task.get("time_start"),
                    }
                    tasks.append(task_info)

            # 2️⃣ Fetch tasks from AsyncResult (finished or filtered by id)
            if task_ids:
                for task_id in task_ids:
                    res = AsyncResult(task_id)
                    task_info = {
                        "task_id": task_id,
                        "name": res.name,
                        "state": res.state,
                        "result": res.result if res.successful() else None,
                        "traceback": res.traceback if res.failed() else None,
                    }
                    tasks.append(task_info)

            # 3️⃣ Apply state filter if requested
            if state_filter:
                tasks = [t for t in tasks if t["state"] == state_filter.upper()]

            return Response({
                "status": "success",
                "count": len(tasks),
                "data": tasks,
            })

        except Exception as e:
            logger.error(f"Error fetching tasks: {e}", exc_info=True)
            return Response({
                "status": "error",
                "message": f"Error fetching tasks: {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScheduledTasksAPIView(APIView, CeleryTaskMonitorMixin):
    """API to get all scheduled tasks"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            inspect = self.get_celery_inspect()
            scheduled_tasks = inspect.scheduled()

            if not scheduled_tasks:
                return Response({
                    'status': 'success',
                    'data': [],
                    'count': 0,
                    'message': 'No scheduled tasks found'
                })

            formatted_tasks = []
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    task_info = self.format_task_info(task)
                    task_info['worker'] = worker
                    formatted_tasks.append(task_info)

            return Response({
                'status': 'success',
                'data': formatted_tasks,
                'count': len(formatted_tasks),
                'workers': list(scheduled_tasks.keys())
            })

        except Exception as e:
            logger.error(f"Error fetching scheduled tasks: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching scheduled tasks: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReservedTasksAPIView(APIView, CeleryTaskMonitorMixin):
    """API to get all reserved tasks"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            inspect = self.get_celery_inspect()
            reserved_tasks = inspect.reserved()

            if not reserved_tasks:
                return Response({
                    'status': 'success',
                    'data': [],
                    'count': 0,
                    'message': 'No reserved tasks found'
                })

            formatted_tasks = []
            for worker, tasks in reserved_tasks.items():
                for task in tasks:
                    task_info = self.format_task_info(task)
                    task_info['worker'] = worker
                    formatted_tasks.append(task_info)

            return Response({
                'status': 'success',
                'data': formatted_tasks,
                'count': len(formatted_tasks),
                'workers': list(reserved_tasks.keys())
            })

        except Exception as e:
            logger.error(f"Error fetching reserved tasks: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching reserved tasks: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskDetailAPIView(APIView):
    """API to get details of a specific task"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, task_id):
        try:
            result = AsyncResult(task_id, app=current_app)

            task_info = {
                'task_id': task_id,
                'state': result.state,
                'status': result.status,
                'result': result.result,
                'info': result.info,
                'successful': result.successful(),
                'failed': result.failed(),
                'ready': result.ready(),
                'date_done': result.date_done.isoformat() if result.date_done else None,
                'traceback': result.traceback,
                'children': [child.id for child in result.children] if result.children else [],
                'parent': result.parent.id if result.parent else None,
            }

            return Response({
                'status': 'success',
                'data': task_info
            })

        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching task details: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkerStatsAPIView(APIView):
    """API to get worker statistics"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            inspect = current_app.control.inspect()

            # Get worker stats
            stats = inspect.stats()
            active = inspect.active()
            registered = inspect.registered()

            worker_info = []

            if stats:
                for worker_name, worker_stats in stats.items():
                    worker_data = {
                        'name': worker_name,
                        'status': 'online',
                        'active_tasks': len(active.get(worker_name, [])) if active else 0,
                        'registered_tasks': len(registered.get(worker_name, [])) if registered else 0,
                        'total_tasks': worker_stats.get('total', {}),
                        'rusage': worker_stats.get('rusage', {}),
                        'clock': worker_stats.get('clock', 0),
                        'pool': worker_stats.get('pool', {}),
                        'broker': worker_stats.get('broker', {}),
                    }
                    worker_info.append(worker_data)

            return Response({
                'status': 'success',
                'data': worker_info,
                'count': len(worker_info)
            })

        except Exception as e:
            logger.error(f"Error fetching worker stats: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching worker statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisteredTasksAPIView(APIView):
    """API to get all registered tasks across workers"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            inspect = current_app.control.inspect()
            registered_tasks = inspect.registered()

            if not registered_tasks:
                return Response({
                    'status': 'success',
                    'data': [],
                    'message': 'No registered tasks found'
                })

            all_tasks = set()
            worker_tasks = {}

            for worker, tasks in registered_tasks.items():
                worker_tasks[worker] = tasks
                all_tasks.update(tasks)

            return Response({
                'status': 'success',
                'data': {
                    'all_registered_tasks': sorted(list(all_tasks)),
                    'worker_tasks': worker_tasks,
                    'total_unique_tasks': len(all_tasks)
                }
            })

        except Exception as e:
            logger.error(f"Error fetching registered tasks: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching registered tasks: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class TaskControlAPIView(View):
    """API to control tasks (revoke, terminate, etc.)"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            task_id = data.get('task_id')

            if not action or not task_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Both action and task_id are required'
                }, status=400)

            if action == 'revoke':
                # Revoke task
                current_app.control.revoke(task_id, terminate=data.get('terminate', False))
                return JsonResponse({
                    'status': 'success',
                    'message': f'Task {task_id} revoked successfully'
                })

            elif action == 'terminate':
                # Terminate task
                current_app.control.revoke(task_id, terminate=True)
                return JsonResponse({
                    'status': 'success',
                    'message': f'Task {task_id} terminated successfully'
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Error controlling task: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error controlling task: {str(e)}'
            }, status=500)


from kombu import Connection, Queue, Exchange


class QueueLengthAPIView(APIView):
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            with Connection(current_app.conf.broker_url) as conn:
                exchange = Exchange("celery", type="direct")
                queue = Queue(
                    name="celery",
                    exchange=exchange,
                    routing_key="celery",
                    durable=True,
                )

                try:
                    bound_queue = queue(conn)
                    length = bound_queue.queue_declare(passive=True).message_count

                    return Response({
                        "status": "success",
                        "data": {
                            "queue_name": "celery",
                            "length": length,
                        }
                    })
                except Exception as queue_error:
                    logger.warning(f"Could not get queue length: {queue_error}")
                    return Response({
                        "status": "warning",
                        "data": {
                            "queue_name": "celery",
                            "length": "unavailable",
                            "message": str(queue_error),
                        }
                    })

        except Exception as e:
            logger.error(f"Error fetching queue length: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Error fetching queue length: {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskHistoryAPIView(APIView):
    """API to get task history (requires celery events)"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        # Note: This requires celery events to be enabled
        # Start celery with: celery -A your_project events
        try:
            # This is a basic implementation
            # For full history, you might want to store task results in database
            return Response({
                'status': 'info',
                'message': 'Task history requires celery events monitoring. Enable with: celery -A your_project events',
                'data': []
            })

        except Exception as e:
            logger.error(f"Error fetching task history: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching task history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from datetime import datetime


# Updated view using the utility class
class CeleryDashboardAPIView(APIView):
    """Comprehensive dashboard API that combines all monitoring data"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            inspect = current_app.control.inspect()

            # Get all monitoring data with timeout to prevent hanging
            active_tasks = inspect.active() or {}
            scheduled_tasks = inspect.scheduled() or {}
            reserved_tasks = inspect.reserved() or {}
            worker_stats = inspect.stats() or {}
            registered_tasks = inspect.registered() or {}

            # Count totals
            total_active = sum(len(tasks) for tasks in active_tasks.values())
            total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())
            total_reserved = sum(len(tasks) for tasks in reserved_tasks.values())
            total_workers = len(worker_stats)

            # Get unique registered task types
            all_task_types = set()
            for tasks in registered_tasks.values():
                if isinstance(tasks, list):
                    all_task_types.update(tasks)

            # Worker status summary using utility class
            worker_summary = []
            for worker_name, stats in worker_stats.items():
                worker_active_tasks = active_tasks.get(worker_name, [])
                parsed_stats = CeleryStatsParser.parse_worker_stats(
                    worker_name, stats, worker_active_tasks
                )
                worker_summary.append(parsed_stats)

            # Recent task activity
            dashboard_data = {
                'summary': {
                    'total_workers': total_workers,
                    'total_active_tasks': total_active,
                    'total_scheduled_tasks': total_scheduled,
                    'total_reserved_tasks': total_reserved,
                    'total_task_types': len(all_task_types),
                    'timestamp': datetime.now().isoformat(),
                },
                'workers': worker_summary,
                'task_types': sorted(list(all_task_types)),
                'queue_info': {
                    'name': 'celery',
                    'exchange': 'celery',
                    'routing_key': 'celery',
                },
                'broker_info': {
                    'transport': current_app.conf.broker_url.split('://')[
                        0] if current_app.conf.broker_url else 'unknown',
                    'host': 'configured' if current_app.conf.broker_url else 'not configured',
                }
            }

            return Response({
                'status': 'success',
                'data': dashboard_data
            })

        except Exception as e:
            logger.error(f"Error fetching dashboard data: {str(e)}")

            # Return safe fallback data
            fallback_data = {
                'summary': {
                    'total_workers': 0,
                    'total_active_tasks': 0,
                    'total_scheduled_tasks': 0,
                    'total_reserved_tasks': 0,
                    'total_task_types': 0,
                    'timestamp': datetime.now().isoformat(),
                },
                'workers': [],
                'task_types': [],
                'queue_info': {
                    'name': 'celery',
                    'exchange': 'celery',
                    'routing_key': 'celery',
                },
                'broker_info': {
                    'transport': 'unknown',
                    'host': 'error',
                }
            }

            return Response({
                'status': 'error',
                'message': f'Error fetching dashboard data: {str(e)}',
                'data': fallback_data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# additional_views.py
class TasksByNameAPIView(APIView):
    """API to get tasks by task name"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, task_name):
        try:
            tasks = CeleryMonitorUtils.get_task_info_by_name(task_name)

            return Response({
                'status': 'success',
                'data': tasks,
                'count': len(tasks),
                'task_name': task_name
            })

        except Exception as e:
            logger.error(f"Error fetching tasks for {task_name}: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error fetching tasks: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QueueControlAPIView(APIView):
    """API to control queues (purge, etc.)"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            action = request.data.get('action')

            if action == 'purge':
                success = CeleryMonitorUtils.purge_queue()
                if success:
                    return Response({
                        'status': 'success',
                        'message': 'Queue purged successfully'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'Failed to purge queue'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error controlling queue: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error controlling queue: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkerControlAPIView(APIView):
    """API to control workers"""
    authentication_classes = (ApiKeyAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            action = request.data.get('action')
            destination = request.data.get('destination')  # specific worker or broadcast

            kwargs = {}
            if destination:
                kwargs['destination'] = [destination]

            if action in ['shutdown', 'pool_restart', 'pool_grow', 'pool_shrink', 'add_consumer', 'cancel_consumer']:
                success, message = CeleryMonitorUtils.broadcast_task_control(action, **kwargs)

                if success:
                    return Response({
                        'status': 'success',
                        'message': message
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': message
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                return Response({
                    'status': 'error',
                    'message': f'Unknown action: {action}'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error controlling workers: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error controlling workers: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
