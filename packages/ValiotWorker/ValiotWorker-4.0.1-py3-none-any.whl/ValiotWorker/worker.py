import pydash as __
from pprint import pformat
import time
import json
from typing import Callable, Dict
from json.decoder import JSONDecodeError
import multiprocessing as mp
from multiprocessing import SimpleQueue, Pipe
from datetime import datetime, timedelta
from enum import Enum
from pygqlc import GraphQLClient
from singleton_decorator import singleton
from .Notifications import NotificationBehaviour
from .Logging import log, LogLevel, LogStyle
from . import uploaders
from . import queries
from . import mutations
from . import subscriptions
from .dateHelpers import getUtcDate
from .croniterHelpers import get_croniter
from .redis import WorkerRedis


class QueueType(Enum):
    """Enumeration for all the queue types
    """
    EVENT = 'EVENT'
    FREQUENCY = 'FREQUENCY'
    ON_DEMAND = 'ON_DEMAND'
    SCHEDULE = 'SCHEDULE'
    CONTINUOUS = 'CONTINUOUS'


class JobStatus(Enum):
    """Enumeration for all the job status.
    """
    ABORTED = 'ABORTED'
    ERROR = 'ERROR'
    FINISHED = 'FINISHED'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'


class PollingMode(Enum):
    """Set all the polling modes
    """
    QUERY = 'QUERY'
    SUBSCRIPTION = 'SUBSCRIPTION'


class JobConfigMode(Enum):
    """Enumeration for all the job's configurations
    """
    KEEP = 'KEEP'  # do not touch anything at startup
    SYNC = 'SYNC'  # sync Queues, job configuration, remote logging configuration, etc


DEFAULT_EVENT_CONFIG = {
    "timeout": 5.0,  # seconds to wait, None to run ASAP
    "min_batch": 10,
    "max_batch": 100
}


def safe_pop(data, index=0, default=None):
    """This function makes a safe pop of a list.

    Args:
        data (list): List that want to make a pop
        index (int, optional): Element that want to be poped. Defaults to 0.
        default (optional): Default return if the element doesn't exists. Defaults to None.

    Returns:
        element list: Value of the element poped.
    """
    if len(data) > 0:
        return data.pop(index)
    else:
        return default


@singleton
class ValiotWorker():
    """The ValiotWorker class follows the singleton design pattern. It
      manages all listener logic for any action of a Graphql schema for many queues.

      Attributes:
          queues (dict): Dictonary with all queues. Defaults to
            empty dict.
          eventQueues (dict): Dictonary with all event queues. Defaults to
            empty dict.
          currentQueues (list): List with all active queues.
            Defaults to empty list.
          previousQueues (list): List with all previous queues.
            Defaults to empty list.
          runningJobs (dict): Dictonary with all running jobs. Defaults to
            empty dict.
          lockedJobs (list): List with all locked jobs.
            Defaults to empty list.
          gql (GraphQLClient): GraphQLClient instance.
          worker (string): Worker name.  Defaults to None.
          worker_code (string): Worker id.  Defaults to None.
          pollingMode (PollingMode): Set how will be the polling mode. Defaults to
            Query mode.
          jobConfigMode (JobConfigMode): Set the job configuration. Defaults to KEEP.
          context (Process): Context of a run job. Defaults to None.
          unsubJobCreated (GraphQLClient.sub): GraphQLClient subscriptions. Defaults
            to None.
          useRedis (boolean): Determine to use Redis. Defaults to False.
          redis (WorkerRedis): Instance of a WorkerRedis.
          continuousJobs (list): List of a running job. Defaults to list.
          logginStyle (LogStyle.PREFIX_FIRST_LINE) = LogStyle.PREFIX_FIRST_LINE
          stopLogging (boolean): Set to stop logs.
          loggingProcess (Process): Gets the logs of a process. Defaults to None.
          log (Log): Log message. Defaults to None.
          logQueues (dict): A dictionry with all queues logs.

      Examples:
          >>> <With> clause:
            '''
            import os
            from ValiotWorker import ValiotWorker, PollingMode
            from ValiotWorker.Logging import LogStyle
            from .config import setup_gql
            gql = setup_gql()
            # ! The worker must initialize before Job imports
            worker = ValiotWorker()
            worker.setClient(gql)
            worker.setWorker(os.environ.get('WORKER'))
            worker.setPollingMode(PollingMode.SUBSCRIPTION)
            worker.setLoggingStyle(LogStyle.PREFIX_FIRST_LINE) # default, just for reference
            # ! Import jobs for the worker to recognize them
            from .services.jobs.testComplexOnDemand.__main__ import testComplexOnDemand
            from .services.jobs.testOnDemand.__main__ import testOnDemand
            from .services.jobs.testDirectedNotification.__main__ import testDirectedNotification
            from .services.jobs.testGroupNotification.__main__ import testGroupNotification
            from .services.jobs.testOnEvent.__main__ import testOnEvent
            def main ():
              print('Test suite for Valiot jobs!')
              worker.run(interval=1.0)

            if __name__ == "__main__":
              main()
            '''
    """

    def __init__(self):
        self.queues = {}
        self.eventQueues = {}
        self.currentQueues = []
        self.previousQueues = []
        self.runningJobs = {}
        self.lockedJobs = []
        self.gql = GraphQLClient()
        self.worker = None
        self.worker_code = None
        self.pollingMode = PollingMode.QUERY
        self.jobConfigMode = JobConfigMode.KEEP
        self.context = None
        self.unsubJobCreated = None
        self.useRedis = False
        self.redis = WorkerRedis()
        self.continuousJobs = []
        # logging attributes
        self.loggingStyle = LogStyle.PREFIX_FIRST_LINE
        self.stopLogging = False
        self.loggingProcess = None
        self.log = None
        self.logQueues = {
            'main': SimpleQueue()  # queue for the main thread (Orchestator)
        }

    def setClient(self, client):
        """Set a GraphQLClient instance.

        Args:
            client (GraphQLClient): GraphQLClient instance.
        """
        self.gql = client

    def setWorker(self, worker):
        """Sets a worker code.

        Args:
            worker (string): Worker code.
        """
        self.worker_code = worker

    def setPollingMode(self, mode):
        """Sets Polling Mode

        Args:
            mode (PollingMode): PollingMode option.
        """
        self.pollingMode = mode

    def setJobConfigMode(self, mode):
        """Sets Jobs configuration.

        Args:
            mode (JobConfigMode): JobConfigMode option.
        """
        self.jobConfigMode = mode

    def setLoggingStyle(self, style):
        """Sets logging style.

        Args:
            style (LoggingStyle): LoggingStyle option.
        """
        self.loggingStyle = style

    def setUseRedis(self):
        """Set that worker uses Redis.
        """
        self.useRedis = True

    def job(
        self,
        name,
        alias,
        description='',
        schedule='',
        enabled=None,  # ! PER-WORKER BASIS
        queueType=QueueType.ON_DEMAND,
        query='',
        lockRequired=False,
        notificationBehaviour=NotificationBehaviour.DEFAULT,
        notificationFrequency='',
        notificationSchedule='',
        eventConfig=DEFAULT_EVENT_CONFIG
    ):
        """This fuction is the decorator for a job.

        Args:
            name (string): Job's name.
            alias (string): Job's alias.
            description (str, optional): Job's description. Defaults to ''.
            schedule (str, optional): Job's schedule in cron like format.
              Defaults to ''.
            enabled (boolean, optional): Set if the job is avaible. Defaults to None.
            query (str, optional): Query that will follow the job. Defaults to ''.
            lockRequired (bool, optional): Option that the job can lock.
              Defaults to False.
            notificationBehaviour (NotificationBehaviour, optional): Notification
              behaviour. Defaults to NotificationBehaviour.DEFAULT.
            notificationFrequency (str, optional): Notification frequency Defaults to ''.
            notificationSchedule (str, optional): Notification Schedule in cron like
              format. Defaults to ''.
            eventConfig (optional): Event configuration. Defaults to
              DEFAULT_EVENT_CONFIG.
        """
        def wrap(f):
            parameters = {
                'name': name,
                'alias': alias,
                'description': description,
                'schedule': schedule,
                'type': queueType.value,
                'query': query,
                'lockRequired': lockRequired,
                'function': f,
                "last_run_at": datetime.now()
            }
            if enabled is not None:
                parameters['enabled'] = enabled
            self.queues[name] = parameters
            self.eventQueues[name] = {
                "name": name,
                "function": f,
                "mailbox": [],
                "config": {**DEFAULT_EVENT_CONFIG, **eventConfig},
                "start_time": None  # Time to track, if elapsed and mailbox not empty, trigger event
            }
            return f
        return wrap

    def not_found(self, job_id, update_job, kwargs):
        """This function triggers out if a job fails.

        Args:
            job_id (int): Job ID.
            update_job (method): Job details that will be updated as error.
            kwargs (args): Extra arguments of the job.
        """
        from .Notifications import nextNotifOld
        self.log(LogLevel.ERROR, 'Function not found :(')
        message = 'Funcion no habilitada, favor de contactar a administrador'
        notificationData = {}
        if(nextNotifOld(kwargs['job'])):
            data, errors = self.gql.mutate(mutations.create_notification, {
                'context': 'DANGER',
                'title': f'Error en {kwargs["job"]["queue"]["alias"]}',
                'content': message,
                'metadata': json.dumps({"resolved": False}),
            })
            now = getUtcDate(datetime.now())
            nextNotifDate = now + timedelta(minutes=20)
            notificationData = {
                'id': data['result']['id'],
                'Sent': True,
                'SentAt': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                # 'frequency': '*/2 * * * *', # cron descriptor or empty string
                # cron descriptor or empty string
                'sendNextAt': nextNotifDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        update_job({
            'id': job_id,
            'status': 'ERROR',
            'output': json.dumps({
                'notification': notificationData,
                'message': message
            })
        })

    # Run helpers: -------------------------------
    def getJobData(self, job):
        """This function gets the Job data.

        Args:
            job (object): Job that will tried to run.

        Returns:
            Error, job result.
        """
        NOT_FOUND = {
            'alias': 'Funcion no encontrada',
            'description': 'Funcion ejecutada cuando se trata de llamar Job sin una función registrada',
            'schedule': None,
            'enabled': True,
            'type': QueueType.ON_DEMAND,
            'function': self.not_found,
            "last_run_at": datetime.now()
        }
        fn_name = __.get(job, 'queue.name', 'NOT_FOUND')
        job_dict = __.get(self.queues, fn_name, None)
        return fn_name, job_dict

    def groupQueuesByListenStatus(self, queues):
        """This function groups all queues by their listen status.

        Args:
            queues (dict): All queues.

        Returns:
            lists: Ordered lists.
        """
        not_listened_queues = [
            queue['name']
            for queue in queues
            if not __.get(queue, 'listeners', [])
        ]
        worker_listened_queues = [
            queue['name']
            for queue in queues
            if __.find(
                __.get(queue, 'listeners', []),
                lambda listener: (
                    self.worker_code == __.get(listener, 'worker.code') and
                    __.get(listener, 'enabled')
                )
            )
        ]
        worker_disabled_queues = [
            queue['name']
            for queue in queues
            if __.find(
                __.get(queue, 'listeners', []),
                lambda listener: (
                    self.worker_code == __.get(listener, 'worker.code') and
                    not __.get(listener, 'enabled')
                )
            )
        ]
        return (
            sorted(worker_listened_queues),
            sorted(worker_disabled_queues),
            sorted(not_listened_queues),
        )

    def reportListenedQueuesExhaustive(self):
        """This function makes a exhaustive report with logs of the listened queues.
        """
        (
            listened,
            disabled,
            not_listened
        ) = self.groupQueuesByListenStatus(self.currentQueues)
        self.log(LogLevel.SUCCESS, 'LISTENED Queues:')
        for queue_name in listened:
            self.log(LogLevel.SUCCESS, f"\t{queue_name}")
        if not listened:
            self.log(LogLevel.SUCCESS,
                     f'{self.worker_code} not listening to any Queue')
        self.log(LogLevel.WARNING, 'DISABLED Queues:')
        for queue_name in disabled:
            self.log(LogLevel.WARNING, f"\t{queue_name}")
        if not disabled:
            self.log(LogLevel.WARNING, f'\tNo queues disabled')
        self.log(LogLevel.ERROR, 'NOT LISTENED Queues:')
        for queue_name in not_listened:
            self.log(LogLevel.ERROR, f"\t{queue_name}")
        if not not_listened:
            self.log(LogLevel.INFO, f'\tAll queues listened')

    def reportListenedQueuesDiff(self):
        """This function makes a report with logs of the difference of all queues.
        """
        (
            listened,
            disabled,
            not_listened
        ) = self.groupQueuesByListenStatus(self.currentQueues)
        (
            prev_listened,
            prev_disabled,
            prev_not_listened
        ) = self.groupQueuesByListenStatus(self.previousQueues)
        listened_diff = set(listened) - set(prev_listened)
        disabled_diff = set(disabled) - set(prev_disabled)
        not_listened_diff = set(not_listened) - set(prev_not_listened)
        if listened_diff:
            self.log(LogLevel.SUCCESS, f'NEW LISTENED QUEUES:')
            for queue_name in listened_diff:
                self.log(LogLevel.SUCCESS, f'\t{queue_name}')
        if disabled_diff:
            self.log(LogLevel.WARNING, f'NEW DISABLED QUEUES:')
            for queue_name in disabled_diff:
                self.log(LogLevel.WARNING, f'\t{queue_name}')
        if not_listened_diff:
            self.log(LogLevel.ERROR, f'NEW NOT LISTENED QUEUES:')
            for queue_name in not_listened_diff:
                self.log(LogLevel.ERROR, f'\t{queue_name}')

    def reportQueueChanges(self):
        """This function makes a report with all queues changes.
        """
        if not self.previousQueues:
            # first iteration, report exhaustive lists (Listening, skipping, disabled)
            self.reportListenedQueuesExhaustive()
        else:
            # Check for diffs, and only report that
            self.reportListenedQueuesDiff()

    def abortJob(self, job):
        """This function abort a running job.

        Args:
            job (object): Running job.
        """
        variables = {
            'id': job['id'],
            'status': 'ABORTED'
        }
        data, errors = self.gql.mutate(mutations.update_job, variables)

    def lockQueue(self, queue_name):
        """This function locks a queue.

        Args:
            queue_name (string): Queue's name.

        Returns:
            object: Returns lock object.
        """
        variables = {
            'queue': queue_name,
            'worker': self.worker['code'],
            'active': True,
            'startAt': getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        data, errors = self.gql.mutate(mutations.create_lock, variables)
        lock = __.get(data, 'result')
        queue_index = __.arrays.find_index(
            self.currentQueues, lambda q: q['name'] == queue_name)
        self.currentQueues[queue_index]['locks'].insert(0, lock)
        return lock  # returns lock object

    def unlockQueue(self, queue_name, lock):
        """This function unlocks a queue.

        Args:
            queue_name (string): Queue's name.
            lock (object): Lock object.

        Returns:
            (object): Returns unlocking success status.
        """
        variables = {
            'id': lock['id'],
            'active': False,
            'endAt': getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        data, errors = self.gql.mutate(mutations.update_lock, variables)
        lock = __.get(data, 'result')
        queue_index = __.arrays.find_index(
            self.currentQueues, lambda q: q['name'] == queue_name)
        self.currentQueues[queue_index]['locks'].insert(0, lock)
        return __.get(data, 'successful')  # returns unlocking success status

    def runJob(self, job):
        """This function runs a job

        Args:
            job (object): Job that will run.

        Raises:
            Exception: Missing status of the job.
        """
        # obtiene lock (if needed):
        lock = None
        if job["queue"]["lockRequired"]:
            lock = self.lockQueue(job["queue"]["name"])
        # Obtiene job
        fn_name, job_dict = self.getJobData(job)
        # ! Validates existence of requested job for this worker:
        if not job_dict:
            self.log(
                LogLevel.ERROR,
                f"{fn_name} job not found (it might exist in another branch / parallel universe), skipping..."
            )
            # TODO: Here we can update the job to aborted or something
            return
        self.log(LogLevel.INFO, f"running {fn_name}")
        job_fn = job_dict['function']
        # Obtiene inputs
        if job['input']:
            try:
                if type(job['input']) == dict:
                    kwargs = job['input']
                else:
                    # FALLBACK, attempt to load as a json-encoded string
                    kwargs = json.loads(job['input'])
            except JSONDecodeError as e:
                # falló al leer datos de input, aborta mision
                variables = {
                    'id': int(job['id']),
                    'status': 'ERROR',
                    'output': f'Job input error: {str(e)}'
                }
                uploaders.update_job(variables)
                self.log(LogLevel.ERROR, e)
                return
        else:
            kwargs = job_dict
        # try to run job

        def update_this_job(variables):
            # * funcion de utilidad para actualizar job sin necesidad de conocer su ID
            status = variables.get('status')
            if not status:
                raise Exception('Missing "status" variable')
            # cast to status type to enforce an enumeration value
            status = JobStatus(status)
            # Extract string from enumeration
            safe_vars = {**variables, 'status': status.value}
            # this allows to specify ID inside job for backwards compatibility
            return uploaders.update_job({'id': job['id'], **safe_vars})

        def update_this_context(context):
            return self.gql.mutate(mutations.update_context, {
                'queue': __.get(job, 'queue.name'),
                'context': json.dumps(context)
            })
        src_status_conn, dst_status_conn = Pipe()

        def get_job_status():
            if dst_status_conn.poll():
                job = dst_status_conn.recv()
                return JobStatus(job['jobStatus'])
            return None
        # ! Inyecta a los kwargs el job que se está ejecutando:
        kwargs['job'] = job
        kwargs['job_id'] = job['id']
        # couple of aliases for the same fn
        kwargs['job']['update'] = update_this_job
        # couple of aliases for the same fn
        kwargs['update_job'] = update_this_job
        kwargs['job']['get_status'] = get_job_status
        kwargs['get_job_status'] = get_job_status
        # acceso directo a atributos del queue al que pertenece el job
        kwargs['queue'] = job['queue']
        kwargs['log'] = self.getProcessLoggerFunction(
            queue=job['queue'], job=job)
        kwargs['context'] = __.get(job, 'queue.context', dict())
        kwargs['update_context'] = update_this_context
        kwargs['kwargs'] = {**kwargs}
        variables = {
            'id': int(job['id']),
            'queueName': job['queue']['name'],
            'status': 'RUNNING',
            'lastRunAt': getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        data, errors = self.gql.mutate(
            mutation=mutations.run_job, variables=variables)
        job_success = __.get(data, 'updateJob.successful')
        queue_success = __.get(data, 'updateQueue.successful')
        if job_success and queue_success:
            def safe_fn(**kwargs):
                try:
                    job_fn(**kwargs)
                except TypeError as e:
                    self.log(LogLevel.ERROR,
                             f'Error starting job from queue {fn_name}:\n{str(e)}')
                    self.log(LogLevel.ERROR,
                             f'Did you forget to ignore additional params in the job definition?:')
                    self.log(LogLevel.ERROR, f'@vw.job(...)')
                    self.log(
                        LogLevel.ERROR, f'def my_job(my_param, my_param2, **_) # <== can be **kwargs or **_')
                    self.log(LogLevel.ERROR, f'\t...')
            p = self.context.Process(target=safe_fn, kwargs=(kwargs))
            self.log(LogLevel.INFO, f'started job with ID {job["id"]}')
            p.start()
            self.runningJobs[job['id']] = {
                'process': p,
                'job': {**job},
                'status_src': src_status_conn,
                'status_dst': dst_status_conn
            }
            if lock:
                self.lockedJobs.append({
                    'process': p,
                    'job': job,
                    'lock': lock
                })
        else:
            self.log(LogLevel.ERROR, f'Error starting job (queue={fn_name})')

    def queue_locked(self, queue_name):
        """This function checks if a queue is locked.

        Args:
            queue_name (string): Queue's name

        Returns:
            boolean/object: Returns the information of the locked object.
        """
        queues_by_name = __.group_by(self.currentQueues, 'name')
        current_queue = __.get(queues_by_name, f'{queue_name}.0')
        if not __.get(current_queue, 'lockRequired'):
            return False  # Queue does not require locking
        # locked if last lock is active
        return __.get(current_queue, 'locks.0.active')

    def workerQueueEnabled(self, queue):
        """This function checks if the queue is enable.

        Args:
            queue (object): Queue object

        Returns:
            boolean: Returns if the queue is enable.
        """
        # queue not enabled if: no listener for this queue OR current worker not listening OR listening disabled for this worker
        currentQueue = __.find(
            self.currentQueues,
            lambda cq: queue.get('name') and queue['name'] == cq['name']
        )
        listeners = __.get(currentQueue, 'listeners', [])
        if not listeners:
            return False
        listener = __.find(
            listeners,
            lambda lnr: self.worker_code == __.get(lnr, 'worker.code')
        )
        if not listener:
            return False
        if __.get(listener, 'enabled'):
            return True
        return False

    def processJobs(self):
        """This function manages the process of a Job.
        """
        jobs, errors = self.gql.query(queries.all_jobs, variables={
                                      'worker': self.worker['code']})
        if errors:
            message = errors[0]
            self.log(LogLevel.ERROR, f'Error! msg: {message}')
            return
        if jobs is not None and len(jobs) > 0:
            self.log(LogLevel.WARNING, f"Found {len(jobs)} jobs")
            for job in jobs:
                if self.queue_locked(job['queue']['name']):
                    self.log(LogLevel.ERROR,
                             f"{job['queue']['name']} is LOCKED, job aborted")
                    self.abortJob(job)
                elif self.workerQueueEnabled(job['queue']):
                    self.runJob(job)
                else:
                    self.log(LogLevel.WARNING,
                             f"{job['queue']['name']} is DISABLED, skipping job")
        else:
            self.log(LogLevel.INFO, "Listening to events...")

    def abortStaleJobs(self):
        """This function aborts all stale jobs.
        """
        # * pagination configuration
        workerRegex = f'^{self.worker["code"]}$'  # worker exact match
        limit = 100  # how many jobs to delete in one batch
        cursor = 0  # starting point for each page
        hasNextPage = True
        abortedCount = 0
        pages = 0
        while hasNextPage:
            # * Get staled jobs page
            data, errors = self.gql.query(
                queries.paginate_stale_jobs,
                variables={'worker': workerRegex,
                           'cursor': cursor, 'limit': limit}
            )
            jobs = __.get(data, 'jobs', [])
            cursor = __.get(data, 'pageInfo.endCursor')
            hasNextPage = __.get(data, 'pageInfo.hasNextPage')
            # ! delete 'em jobs
            # * get batch mutation
            BATCH_STALE_DELETE_MUT = mutations.build_batch_stale_mutation(jobs)
            if not BATCH_STALE_DELETE_MUT:
                continue
            # * run mutation
            self.log(LogLevel.WARNING, f'Deleting {len(jobs)} stale jobs...')
            data, errors = self.gql.mutate(BATCH_STALE_DELETE_MUT)
            if errors:
                self.log(LogLevel.ERROR, 'Errors deleting stale jobs:')
                self.log(LogLevel.ERROR, errors)
            self.log(LogLevel.ERROR, f'Deleted {len(jobs)} stale jobs')
            abortedCount += len(jobs)
            pages += 1
        if abortedCount and pages >= 2:
            self.log(LogLevel.ERROR,
                     f'Deleted a total of {abortedCount} stale jobs')
        elif not abortedCount:
            self.log(LogLevel.INFO, 'No stale jobs to delete')

    def updateAvailableQueues(self):
        """This function updates all avaibles queues to the current configuration.
        """
        self.log(LogLevel.SUCCESS, 'Actualizando Jobs disponibles')
        # ! Update each queue / config parameter
        for name, queue in self.queues.items():
            description = __.get(queue, 'description', None)
            schedule = __.get(queue, 'schedule', None)
            query = __.get(queue, 'query', None)
            lockRequired = __.get(queue, 'lockRequired', False)
            variables = {
                'name': queue['name'],
                'alias': queue['alias'],
                'type': queue['type'],
                'lockRequired': lockRequired
            }
            # ! Add optional variables
            if description:
                variables['description'] = description
            if schedule:
                variables['schedule'] = schedule
            if query:
                variables['query'] = query
            # ! Update QUEUE-related config
            data, errors = self.gql.mutate(
                mutation=mutations.upsert_queue,
                variables=variables
            )
            if (errors):
                self.log(LogLevel.ERROR, f'Error actualizando Queue {name}.')
                self.log(LogLevel.ERROR, errors)
            else:
                self.log(LogLevel.SUCCESS,
                         f'Queue {name} actualizado correctamente')

    def updateWorkerQueues(self):
        """This function updates all queues to a current configuration.
        """
        # ! Update WORKER-related config
        # * first, get current configuration (may cause bugs if we create more than one config register, see Many-Many)
        workerQueues, errors = self.gql.query(
            query=queries.get_worker_queues,
            variables={'workerCode': self.worker_code}
        )
        if errors:
            self.log(LogLevel.ERROR, errors)
        # ! Manual Upsert (Not enabled for many-many relationships)
        for name, queue in self.queues.items():
            # ! check whether we should create or update the item:
            workerQueue = __.find(
                workerQueues,
                lambda wk: name == __.get(wk, 'queue.name', None)
            )
            queueEnabled = __.get(queue, 'enabled', False)
            if not workerQueue:
                _, errors = self.gql.mutate(mutations.create_queue_worker, {
                                            'worker': self.worker_code, 'queue': name, 'enabled': queueEnabled})
                if errors:
                    log_lvl = LogLevel.ERROR
                    log_msg = f'Error Creating config for [ {self.worker_code} <=> {name} ]: {errors}'
                else:
                    log_lvl = LogLevel.SUCCESS if queueEnabled else LogLevel.WARNING
                    log_msg = f'Created config for [ {self.worker_code} <=> {name} ] = {"enabled" if queueEnabled else "disabled"}'
            else:
                _, errors = self.gql.mutate(mutations.update_queue_worker, {
                                            'id': workerQueue['id'], 'enabled': queueEnabled})
                if errors:
                    log_lvl = LogLevel.ERROR
                    log_msg = f'Error Updating config for [ {self.worker_code} <=> {name} ]: {errors}'
                else:
                    log_lvl = LogLevel.SUCCESS if queueEnabled else LogLevel.WARNING
                    log_msg = f'Updated config for [ {self.worker_code} <=> {name} ] = {"enabled" if queueEnabled else "disabled"}'
            self.log(log_lvl, log_msg)

    def clearFinishedJobs(self):
        """This function cleans up all finished jobs "cache".
        """
        finished = []
        for job_id, running_job in self.runningJobs.items():
            if not running_job['process'].is_alive():
                finished.append(job_id)
        for f in finished:
            self.runningJobs.pop(f, None)  # remove any finished jobs

    def unlockFinishedJobs(self, force=False):
        """This function updates all finished jobs to unlock them..

        Args:
            force (bool, optional): Option to force the unlock update. Defaults to False.
        """
        unlocked = []
        _log = log if force else self.log
        for i, job_lock in enumerate(self.lockedJobs):
            if not job_lock['process'].is_alive() or force:
                if self.unlockQueue(job_lock['job']['queue']['name'], job_lock['lock']):
                    _log(LogLevel.SUCCESS,
                         f'{job_lock["job"]["queue"]["name"]} UNLOCKED')
                    unlocked.append(i)
                else:
                    _log(LogLevel.ERROR,
                         f'error unlocking {job_lock["job"]["queue"]["name"]}')
        if unlocked:
            unlocked.reverse()
            for u in unlocked:
                self.lockedJobs.pop(u)

    def runTimedOutEvents(self):
        """This function checks all queue that are in time out.
        """
        current_time = time.time()
        for queue in self.eventQueues.values():
            if not queue['start_time'] or len(queue['mailbox']) == 0:
                continue  # nothing to run
            elapsed = current_time - queue['start_time']
            if elapsed >= queue['config']['timeout']:
                self.log(LogLevel.WARNING,
                         f'Event {queue["name"]} timed out, running...')
                self.runEvent(queue['name'])

    def runFrequencyQueues(self):
        """
        This function checks if it has elapsed enough time since the last attempt to run this queue.
        It takes into account the last time a job of this queue was created,
        rather than when was the last time the job RAN, this enforces only 1 attempt per interval.
        """
        from pytz import timezone
        utc = timezone("UTC")
        queuesByType = __.group_by(self.currentQueues, 'type')
        freqQueues = __.get(queuesByType, 'FREQUENCY', default=[])
        # self.log(LogLevel.WARNING, f'checking {len(freqQueues)} frequency queues')
        for queue in freqQueues:
            lastRunAt = __.get(
                queue,
                # ! get from job.updatedAt, rather than queue.lastRunAt itself (see description of this method)
                'jobs.0.updatedAt',
                # ! Default: if it has never been ran, set the lastRunAt as a very old date (forces next run)
                "2000-01-01T00:00:00Z"
            )
            lastRunDate = datetime.strptime(lastRunAt, "%Y-%m-%dT%H:%M:%SZ")
            lastRunDate = utc.localize(lastRunDate)
            now = getUtcDate(datetime.now())
            cron_iter = get_croniter(queue['schedule'], now)
            nextRunAt = [cron_iter.get_next(datetime)
                         for _ in [0, 1]]  # next and nexter dates
            # validate if next date is met:
            elapsedFromLastRun = (
                now - lastRunDate).total_seconds() / 60.0  # in minutes
            freq = (nextRunAt[1] - nextRunAt[0]
                    ).total_seconds() / 60.0  # in minutes
            if (elapsedFromLastRun > freq):
                # ! Run the frequency job!
                if self.workerQueueEnabled(queue):
                    self.gql.mutate(
                        mutation=mutations.create_job,
                        variables={
                            'queueName': queue['name'],
                            'worker': self.worker['code']
                        }
                    )

    def registerJobCreatedSubscription(self):
        """Registers JobCreated subscription that will call certain job when activated"""
        def runOnDemandJob(data):
            """Callback to run when job is created.
            It checks if the job corresponds to active worker or is a dummy subscription call
            """
            job = __.get(data, 'result')
            if not job:
                return  # Possibly a job for another worker
            if self.queue_locked(job['queue']['name']):
                self.log(LogLevel.ERROR,
                         f"{job['queue']['name']} is LOCKED, job aborted")
                self.abortJob(job)
            elif self.workerQueueEnabled(job['queue']):
                self.runJob(job)
            else:
                self.log(LogLevel.WARNING,
                         f"{job['queue']['name']} is DISABLED, skipping job")

        self.unsubJobCreated = self.gql.subscribe(
            query=subscriptions.JOB_CREATED,
            variables={'workerCode': self.worker['code']},
            callback=runOnDemandJob)
        if (self.unsubJobCreated):
            self.log(LogLevel.SUCCESS, 'SUBSCRIBED TO JOB CREATIONS')
        else:
            self.log(LogLevel.ERROR, 'ERROR SUBSCRIBING TO JOB CREATIONS')

    def runEvent(self, queue_name):
        '''
        This wrapper ensures that whenever runEvent is called, the event is cleared
        '''
        cleanup = self.actuallyRunEvent(queue_name)
        # Move mailbox data and clear it
        if cleanup:
            self.eventQueues[queue_name]["mailbox"] = []
            self.eventQueues[queue_name]["start_time"] = None  # Clear timeout

    def actuallyRunEvent(self, queue_name):
        """Runs job of type ON_EVENT

        Parameters
        ----------
        queue_name : string
          Name of the queue to run
        Returns
        -------
        boolean
          True if a cleanup should be performed (event cleanup)
          False if cleanup should be skipped (to run event at a later point)
        """
        queuesByName = __.group_by(self.currentQueues, 'name')
        currentQueue = __.get(queuesByName, f'{queue_name}.0')
        if self.queue_locked(currentQueue['name']):
            self.log(LogLevel.WARNING,
                     f"{currentQueue['name']} is LOCKED, event postponed")
            return False
        elif not self.workerQueueEnabled(currentQueue):
            self.log(
                LogLevel.WARNING, f'Event triggered for {queue_name} but Queue not enabled, skipping...')
            return True
        data = self.eventQueues[queue_name]["mailbox"]
        # ! try to run job
        # obtiene lock (if needed):
        lock = None
        if currentQueue["lockRequired"]:
            lock = self.lockQueue(currentQueue["name"])
        # Crea job asociado a evento
        response, errors = self.gql.mutate(
            mutation=mutations.run_event_job,
            variables={
                'queueName': queue_name,
                'worker': self.worker['code'],
                'lastRunAt': getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        if errors:
            self.log(LogLevel.ERROR, f'Error starting event:\n{errors}')
            return True
        job = __.get(response, 'job.result')

        def update_this_job(variables):
            # * funcion de utilidad para actualizar job sin necesidad de conocer su ID
            status = variables.get('status')
            if not status:
                raise Exception('Missing "status" variable')
            # cast to status type to enforce an enumeration value
            status = JobStatus(status)
            # Extract string from enumeration
            safe_vars = {**variables, 'status': status.value}
            # this allows to specify ID inside job for backwards compatibility
            return uploaders.update_job({'id': job['id'], **safe_vars})

        def update_this_context(context):
            return self.gql.mutate(mutations.update_context, {
                'queue': __.get(currentQueue, 'name'),
                'context': json.dumps(context)
            })
        src_status_conn, dst_status_conn = Pipe()

        def get_job_status():
            if dst_status_conn.poll():
                job = dst_status_conn.recv()
                return JobStatus(job['jobStatus'])
            return None
        # ! Inyecta a los kwargs el job que se está ejecutando:
        kwargs = {
            'job_id': job['id'],
            'job': {**job, 'update': update_this_job, 'get_status': get_job_status},
            'update_job': update_this_job,
            'get_job_status': get_job_status,
            'queue': currentQueue,
            'context': __.get(currentQueue, 'context', dict()),
            'update_context': update_this_context,
            'data': data,
            'log': self.getProcessLoggerFunction(queue=currentQueue, job=job)
        }
        kwargs['kwargs'] = {**kwargs}

        def safe_fn(**kwargs):
            try:
                self.eventQueues[queue_name]['function'](**kwargs)
            except TypeError as e:
                self.log(
                    LogLevel.ERROR, f'Error starting job from queue {queue_name}:\n{str(e)}')
                self.log(
                    LogLevel.ERROR, f'Did you forget to ignore additional params in the job definition?:')
                self.log(LogLevel.ERROR, f'@vw.job(...)')
                self.log(
                    LogLevel.ERROR, f'def my_job(my_param, my_param2, **_) # <== can be **kwargs or **_')
                self.log(LogLevel.ERROR, f'\t...')
        p = self.context.Process(target=safe_fn, kwargs=(kwargs))
        p.start()
        self.runningJobs[job['id']] = {
            'process': p,
            'job': {**job},
            'status_src': src_status_conn,
            'status_dst': dst_status_conn
        }
        if lock:
            self.lockedJobs.append({
                'process': p,
                'job': {**job, 'queue': {**currentQueue}},
                'lock': lock
            })
        return True

    def getOnQueueEventCallback(self, queue: Dict[str, str]) -> Callable:
        """Wrap the onEventTriggered with a given queue data estructure for labeling purposes

        Args:
            queue (Dict[str, str]): Data structure returned by self.queues
        """
        def onEventTriggered(data):
            """Callback to execute on every event triggered of the same type.
            This callback performs a check to know if enough data (or time)
            has elapsed and thus the Job has to be executed with the current chunk of data

            Parameters
            ----------
            data : any
                Data received from the event
            """
            if not self.workerQueueEnabled(queue):
                return  # Skipping event
            if len(self.eventQueues[queue["name"]]["mailbox"]) == 0:
                self.log(
                    LogLevel.WARNING, f'EVENT { queue["name"] } TRIGGERED, BUILDING BATCH')
                self.eventQueues[queue["name"]]["start_time"] = time.time()
            self.eventQueues[queue["name"]]["mailbox"].append(data)
            if len(self.eventQueues[queue["name"]]["mailbox"]) >= self.eventQueues[queue["name"]]['config'][
                    'max_batch']:
                """Run event only if event surpassed the upper data limit"""
                self.runEvent(queue["name"])
        return onEventTriggered

    def registerEventJobs(self):
        """This function registers a new event job.
        """
        queuesByType = __.group_by(self.queues.values(), 'type')
        eventQueues = __.get(queuesByType, 'EVENT', default=[])
        for queue in eventQueues:
            unsub = self.gql.subscribe(
                query=queue['query'],
                callback=self.getOnQueueEventCallback(queue))
            if (unsub):
                self.log(
                    LogLevel.SUCCESS, f'REGISTERED LISTENER FOR EVENT QUEUE { queue["name"] }')
            else:
                self.log(
                    LogLevel.ERROR, f'ERROR REGISTERING LISTENER FOR EVENT QUEUE { queue["name"] }')

    def registerJobUpdatesListener(self):
        """This function registers for all jobs updates.
        """
        def onJobUpdated(data):
            successful = __.get(data, 'successful')
            job = __.get(data, 'result')
            # check if update even succeeded
            if not job or not successful:
                return
            # check if updated job matches any currently running
            job_running = self.runningJobs.get(job['id'], None)
            if not job_running:
                return
            # at this point we are certain the updated job is running, update structure to inform the job:
            status_conn = self.runningJobs[job['id']]['status_src']
            status_conn.send(job)
        unsub = self.gql.subscribe(
            query=subscriptions.JOB_UPDATED, callback=onJobUpdated)
        if (unsub):
            self.log(LogLevel.SUCCESS, f'REGISTERED LISTENER FOR JOB UPDATES')
        else:
            self.log(LogLevel.ERROR,
                     f'ERROR REGISTERING LISTENER FOR JOB UPDATES')

    def registerContinuousJobs(self):
        """This function registers for all continues jobs.
        """
        queuesByType = __.group_by(self.queues.values(), 'type')
        shedeuleQueues = __.get(queuesByType, 'CONTINUOUS', default=[])
        for shedeuleQueue in shedeuleQueues:
            queue_name = __.get(shedeuleQueue, 'name', None)
            if queue_name:
                self.continuousJobs.append(queue_name)
                queueLocks, errors = self.gql.query(queries.get_queueLocks, variables={
                    "workerCode": self.worker_code, "queueName": queue_name})
                if errors:
                    self.log(LogLevel.ERROR,
                             f'Error get_queueLocks:\n{errors}')
                    continue
                if queueLocks:
                    self.log(
                        LogLevel.WARNING, f'{queue_name} queue (CONTINUOUS type) has queueLocks')
                    for queueLock in queueLocks:
                        variables = {
                            'id': __.get(queueLock, 'id', None),
                            'active': False,
                            'endAt': getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                        _, errors = self.gql.mutate(
                            mutations.update_lock, variables)
                        if errors:
                            self.log(LogLevel.ERROR,
                                     f'Error update_lock:\n{errors}')

        if self.continuousJobs:
            self.log(LogLevel.SUCCESS, 'REGISTERED Continuous Queues:')
            for continuousJob in self.continuousJobs:
                self.log(LogLevel.SUCCESS, f"\t{continuousJob}")

    def monitorContinuousJobs(self):
        """This function checks all continous jobs.
        """
        running_jobs_names = [__.get(running_job, 'job.queue.name', None)
                              for _, running_job in self.runningJobs.items()]
        for continuousJob in self.continuousJobs:
            if not continuousJob in running_jobs_names and self.queues[continuousJob]['enabled']:
                self.log(LogLevel.WARNING,
                         f'Continuous Job {continuousJob} is not running')
                self.log(LogLevel.INFO, f'Creating Job {continuousJob} ...')
                _, errors = self.gql.mutate(mutation=mutations.create_job,
                                            variables={'queueName': continuousJob, 'worker': self.worker['code']})
                if errors:
                    self.log(LogLevel.ERROR, f'Error create_job:\n{errors}')

    def getProcessLoggerFunction(self, queue=None, job=None):
        """Logs to STDOUT formatted to help get helpful information

        Parameters
        ----------
        queue : int, optional
          ID for the queue sending this message, by default 0
        job : int, optional
          ID for the job sending this message, by default 0
        """
        job_zero_padding = len(str(__.get(self.worker, 'jobs.0.id')))
        # no need to pass as argument, will always be the same
        W = str(self.worker["id"]).zfill(2)
        Q = str(__.get(queue, 'id', 0)).zfill(3)
        J = str(__.get(job, 'id', 0)).zfill(job_zero_padding)
        log_queue_key = __.get(queue, 'name', 'main')
        log_queue = self.logQueues[log_queue_key]
        if self.loggingStyle == LogStyle.PREFIX_ALL_LINES:
            def sendLogToQueue(level, message):
                D = getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
                msgs = message.split('\n')
                for msg in msgs:
                    log_queue.put({
                        'level': level,
                        'content': f'[D={D}/W={W}/Q={Q}/J={J}] - {msg}'
                    })
        else:
            def sendLogToQueue(level, message):
                D = getUtcDate(datetime.now()).strftime("%Y-%m-%dT%H:%M:%SZ")
                log_queue.put({
                    'level': level,
                    'content': f'[D={D}/W={W}/Q={Q}/J={J}] - {message}'
                })
        return sendLogToQueue

    def startLoggingLoop(self):
        """This function has the responsability to make a log loop for any event.
        """
        self.log = self.getProcessLoggerFunction()
        # FN DEFINITION --------------------------

        def loggingLoop():
            try:
                while not self.stopLogging:
                    # * check mailbox for every queue
                    # * log as many messages from same queue as possible
                    # TODO: May set a limit to this, in message count or timeout for other queues)
                    # ! Send messages to log-upload queue
                    # ! flag as CREATE or UPSERT for retention or real-time visualization only
                    for _, log_queue in self.logQueues.items():
                        while not log_queue.empty():
                            msg = log_queue.get()
                            log(msg['level'], msg['content'])
            except KeyboardInterrupt:
                log(LogLevel.WARNING, 'Logging stopped due to keyboard interrupt')
            log(LogLevel.WARNING, 'Logging loop stopped')
        # END FN DEFINITION --------------------------
        # Create Queues for each queue:
        for queue_name, _ in self.queues.items():
            self.logQueues[queue_name] = SimpleQueue()
        self.loggingProcess = self.context.Process(target=loggingLoop)
        self.loggingProcess.start()
        self.log(LogLevel.SUCCESS, 'Logging loop started')

    def stopLoggingLoop(self):
        """This function stops de logging loop.
        """
        self.stopLogging = True
        self.loggingProcess.join()

    def eventLoop(self, interval=1.0):
        """This function manages all generic worker activities.

        Args:
            interval (float, optional): Interval time of each loop. Defaults to 1.0.
        """
        try:
            currentQueues, errors = self.gql.query(
                queries.all_queues_w_listeners)
            if (errors):
                self.log(LogLevel.ERROR, f'errors: {errors}')
                return
            self.currentQueues = currentQueues
            self.reportQueueChanges()
            self.clearFinishedJobs()
            self.unlockFinishedJobs()
            self.runFrequencyQueues()
            self.runTimedOutEvents()
            # TODO: sendReminders(queues)
            if self.pollingMode == PollingMode.QUERY:
                self.processJobs()
            else:
                self.log(LogLevel.INFO, 'Listening to events...')
            if self.useRedis:
                self.redis.monitorRedisSubscriptions()
            self.monitorContinuousJobs()
        except Exception as e:
            self.log(LogLevel.ERROR, f"Error in worker's event loop!")
            self.log(LogLevel.ERROR, f'e: {e}')
        self.previousQueues = self.currentQueues
        time.sleep(interval)

    def getWorker(self):
        """This function gets the worker information.
        """
        worker, errors = self.gql.query_one(
            queries.get_worker,
            {'code': self.worker_code}
        )
        if errors:
            log(LogLevel.ERROR, errors)
            raise Exception('Worker not found')
        self.worker = worker

    def run(self, interval=1.0):
        """This function turns on the worker.

        Args:
            interval (float, optional): Time interval of each eventloop.
              Defaults to 1.0.
        """
        self.context = mp.get_context('fork')
        self.getWorker()
        self.startLoggingLoop()
        self.abortStaleJobs()
        if (self.jobConfigMode == JobConfigMode.SYNC):
            self.updateAvailableQueues()
            self.updateWorkerQueues()
        else:
            self.log(
                LogLevel.INFO, 'No config sync performed. If required, set jobConfigMode to SYNC')
        if (self.pollingMode == PollingMode.SUBSCRIPTION):
            self.registerJobCreatedSubscription()
        self.registerEventJobs()
        self.registerJobUpdatesListener()
        if self.useRedis:
            self.redis.setLog(self.log)
            self.redis.initializeRedis()
        self.registerContinuousJobs()
        while 1:
            try:
                self.eventLoop(interval=interval)
            except KeyboardInterrupt:
                log(LogLevel.WARNING, "\nuser's stop signal, exiting...")
                self.stopLoggingLoop()
                self.unlockFinishedJobs(force=True)
                self.gql.close()
                break
