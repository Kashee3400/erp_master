from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    name = serializers.CharField()
    state = serializers.CharField()
    received = serializers.FloatField(allow_null=True)
    started = serializers.FloatField(allow_null=True)
    timestamp = serializers.FloatField(allow_null=True)
    runtime = serializers.FloatField(allow_null=True)
    result = serializers.JSONField(allow_null=True)
    exception = serializers.CharField(allow_null=True)
    traceback = serializers.CharField(allow_null=True)
    args = serializers.ListField(default=list)
    kwargs = serializers.DictField(default=dict)
    eta = serializers.CharField(allow_null=True)
    expires = serializers.CharField(allow_null=True)
    retries = serializers.IntegerField(default=0)
    worker = serializers.CharField(allow_blank=True)
    queue = serializers.CharField(default='erp_master_queue')


class WorkerSerializer(serializers.Serializer):
    name = serializers.CharField()
    status = serializers.CharField()
    active_tasks = serializers.IntegerField()
    registered_tasks = serializers.IntegerField()
    total_tasks = serializers.DictField()
    rusage = serializers.DictField()
    clock = serializers.IntegerField()
    pool = serializers.DictField()
    broker = serializers.DictField()
