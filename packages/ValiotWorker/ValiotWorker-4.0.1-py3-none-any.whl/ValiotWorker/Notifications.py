from pprint import pprint
from enum import Enum
from datetime import datetime
from pytz import timezone
import pydash
from pygqlc import GraphQLClient
from . import queries
from . import mutations
from .Logging import log, LogLevel
from .mutations import update_notification_metadata
from .dateHelpers import getUtcDate
from .croniterHelpers import get_croniter
gql = GraphQLClient()
# * for correct time comparisons between server and client
utc = timezone('UTC')


class NotificationBehaviour(Enum):
    DEFAULT = 'DEFAULT'
    PERSISTENT = 'PERSISTENT'


class NotificationType(Enum):
    PRIMARY = 'PRIMARY'
    SECONDARY = 'SECONDARY'
    INFO = 'INFO'
    SUCCESS = 'SUCCESS'
    WARNING = 'WARNING'
    DANGER = 'DANGER'


reminders = {}
reminderCheckers = {}


def reminder(name):
    def wrap(f):
        reminders[name] = f  # ! function that will get the reminder content
        return f
    return wrap


def reminderChecker(name):
    def wrap(f):
        # ! function that will eval if a notification must be sent again
        reminderCheckers[name] = f
        return f
    return wrap


def defaultReminderChecker(schedule, now, lastSentDate):
    log(LogLevel.DEBUG, 'Running default reminder checker')
    log(LogLevel.DEBUG, schedule)
    log(LogLevel.DEBUG, now)
    log(LogLevel.DEBUG, lastSentDate)
    cron_iter = get_croniter(schedule, now)
    nextRunAt = [cron_iter.get_next(datetime)
                 for _ in [0, 1]]  # next and nexter dates
    # validate if next date is met:
    elapsedFromLastRun = (
        now - lastSentDate).total_seconds() / 60.0  # in minutes
    freq = (nextRunAt[1] - nextRunAt[0]).total_seconds() / 60.0  # in minutes
    if (elapsedFromLastRun > freq):
        log(LogLevel.DEBUG, 'Return true: Frequency for next notification met')
        return True
    log(LogLevel.DEBUG, 'Return false: Frequency not met')
    return False  # Frequency not met


def defaultReminder(queue):
    return {
        'title': 'Recordatorio',
        'content': f'Hay una notificación sin resolver para {queue["alias"]}',
        'context': NotificationType.INFO.value,
        'link': 'monitors',
        'linkText': 'Ir a Monitores'
    }


def resolve(queue):
    import json
    # * check if there is any notification to resolve
    notificationId = pydash.get(queue, 'query.notification.id', None)
    if (notificationId):
        # * if so, resolve notification
        metadata = json.dumps({'resolved': True})
        response, errors = gql.mutate(
            mutation=update_notification_metadata,
            variables={
                'id': parseInt(notificationId),
                'metadata': metadata
            }
        )
        if (errors):
            log(LogLevel.ERROR, 'Error resolving notification!:')
            log(LogLevel.ERROR, errors)


# ! Validate if a new notification must be sent
'''
Job with notification output example:
{
  "id": "590",
  "queue": {
    "id": "17",
    "name": "BLABLA_TEST"
  },
  "progress": 0,
  "jobStatus": "ERROR",
  "input": "{}",
  "output": {
    "notification": {
      "id": "123"
      "Sent": true, 
      "SentAt": "2019-07-26T12:51:16Z", 
      "frequency": ", # cron descriptor or empty string
      "sendNextAt": "2019-07-26T12:51:16Z"
    },
    "message": "Funcion no habilitada, favor de contactar a administrador"},
  "insertedAt": "2019-07-26T12:51:14Z"
}
'''
# ! deprecated, for reference only


def nextNotifOld(job, worker=None):
    log(LogLevel.DEBUG, 'Debugging nextNotification')
    queueName = pydash.get(job, 'queue.name')
    queue, errors = gql.query(queries.get_queue_last_jobs, {
        'name': queueName,
        'count': 2,
        'worker': worker
    })
    prev_job_output = pydash.get(queue, 'jobs.1.output')
    try:
        prev_job_output = json.loads(prev_job_output)
    except Exception as e:
        prev_job_output = {}
    notif_data = pydash.get(prev_job_output, 'notification')
    if not prev_job_output or not notif_data:
        log(LogLevel.DEBUG, 'Return true: No notification info provided')
        return True  # * if no notification info is provided, the validation passes
    # * If Notification info is provided, get notification
    log(LogLevel.DEBUG, notif_data)
    notification, errors = gql.query(queries.get_notification, {
                                     'id': int(notif_data['id'])})
    if (errors):
        log(LogLevel.ERROR, f'Error al leer notificacion: {errors}')
        return True
    # * If the notification is marked as resolved, you can send notifications again
    metadata = pydash.get(notification, 'metadata', "{}")
    log(LogLevel.DEBUG, f'metadata: {metadata}')
    try:
        metadata = json.loads(metadata)
    except Exception as e:
        metadata = {}
    resolved = pydash.get(metadata, 'resolved', True)
    if resolved:
        log(LogLevel.DEBUG, 'Return true: Previous notification resolved already')
        return True
    # * If not resolved (or not resolvable), check if the time has come to send a new notification
    now = getUtcDate(datetime.now())
    sendNextAt = pydash.get(notif_data, 'sendNextAt')
    log(LogLevel.DEBUG, f'sendNextAt: {sendNextAt}')
    if (sendNextAt):
        sendNextDate = datetime.strptime(sendNextAt, "%Y-%m-%dT%H:%M:%SZ")
        sendNextDate = utc.localize(sendNextDate)
        if now > sendNextDate:
            log(LogLevel.DEBUG, 'Return true: Next notification date Met')
            return True
        else:
            log(LogLevel.DEBUG, 'Return false: Next notification date Not yet met')
            return False
    frequency = pydash.get(notif_data, 'frequency')
    if (frequency):
        sentAt = pydash.get(notif_data, 'sentAt')
        sentAtDate = datetime.strptime(sentAt, "%Y-%m-%dT%H:%M:%SZ")
        sentAtDate = utc.localize(sentAtDate)
        croniter = get_croniter(frequency, now)
        nextRunAt = [cron_iter.get_next(datetime)
                     for _ in [0, 1]]  # next and nexter dates
        # validate if next date is met:
        elapsedFromLastRun = (
            now - sentAtDate).total_seconds() / 60.0  # in minutes
        freq = (nextRunAt[1] - nextRunAt[0]
                ).total_seconds() / 60.0  # in minutes
        if (elapsedFromLastRun > freq):
            log(LogLevel.DEBUG, 'Return true: Frequency for next notification met')
            return True
        log(LogLevel.DEBUG, 'Return false: Frequency not met')
        return False  # Frequency not met
    log(LogLevel.ERROR, 'Weird notification case, should not happen :(')
    log(LogLevel.ERROR, prev_job_output)
    log(LogLevel.ERROR, notification)
    return False


def validateNextNotification(queue):
    import json
    # ! Get required data and Clean data validations:
    checker = pydash.get(reminderCheckers, queue['name'], None)
    if not reminderChecker:
        log(LogLevel.ERROR, "No es posible enviar notificaciones inteligentes sin configurar una funcion @Notifications.reminder")
        return {'ready': False}
    queueConfigString = pydash.get(queue, 'query', "{}")
    if not queueConfigString:
        log(LogLevel.DEBUG, "With no queue configuration data, is assumed to be ok to send a new notification")
        return {'ready': True, 'isReminder': False}
    queueConfig = json.loads(queueConfigString)
    notificationData = pydash.get(queueConfig, 'notification', {})
    if not notificationData:
        log(LogLevel.DEBUG, "With no notification data, is assumed to be ok to send a new notification")
        return {'ready': True, 'isReminder': False}
    # * if notification data available, get it and check for resolvedness:
    lastNotification, errors = gql.query(queries.get_notification, {
                                         'id': int(notificationData['id'])})
    if (errors):
        log(LogLevel.ERROR, f'Error al leer notificacion: {errors}')
        return {'ready': False}
    # * If the notification is marked as resolved, you can send notifications again
    metadata = pydash.get(lastNotification, 'metadata', "{}")
    try:
        metadata = json.loads(metadata)
    except Exception as e:
        metadata = {}
    resolved = pydash.get(metadata, 'resolved', True)
    if resolved:
        log(LogLevel.DEBUG, 'Return true: Previous notification resolved already')
        return {'ready': True, 'isReminder': False}
    log(LogLevel.DEBUG, 'Notification not resolved yet, evaluating reminderChecker')
    # * First, we get the two possible dates:
    lastReminderAt = pydash.get(queueConfig, 'reminder.insertedAt', None)
    lastNotificationAt = pydash.get(lastNotification, 'insertedAt', None)
    # ! if a reminder was sent recently, pick it over the last notification
    lastSentAt = lastReminderAt if lastReminderAt else lastNotificationAt
    if lastReminderAt:
        log(LogLevel.DEBUG,
            f'reminder has been sent, last time was: {lastReminderAt}')
    else:
        log(LogLevel.DEBUG,
            f'reminder has not been sent, last notification was at: {lastNotificationAt}')
    # get dates for comparisons
    now = getUtcDate(datetime.now())
    lastSentDate = datetime.strptime(lastSentAt, "%Y-%m-%dT%H:%M:%SZ")
    lastSentDate = utc.localize(lastSentDate)
    mustRemind = checker(now, lastSentDate)
    return {'ready': mustRemind, 'isReminder': True}


def smartNotification(queue, content):
    """This function makes an action notification.

    Args:
        queue (str): Action that the notification do.
        content (dic): Variables that complete the message of the notification.
    """
    import json
    queueName = pydash.get(queue, 'name')
    # ! Validate if new notification must be sent
    nextNotification = validateNextNotification(queue)
    if not nextNotification['ready']:
        return
    isReminder = nextNotification['isReminder']
    # ! injects the resolved field to metadata only when this is the first notification
    metadata = json.dumps({'resolved': False} if not isReminder else {})
    variables = {}
    if isReminder:
        _reminder = reminders[queueName](queue)
        variables = {
            **_reminder,
            'metadata': metadata
        }
    else:
        variables = {
            **content,
            'metadata': metadata
        }
    response, errors = gql.mutate(mutations.create_notification, variables)
    if errors:
        log(LogLevel.ERROR, 'Error sending smart notification:')
        log(LogLevel.ERROR, errors)
        return
    log(LogLevel.SUCCESS, 'Notification sent successfully:')
    notification = pydash.get(response, 'result')
    # * get queue metadata and inject notification data:
    queue_meta_string = pydash.get(queue, 'query', "{}")
    queue_metadata = json.loads(
        queue_meta_string if queue_meta_string else "{}")
    if isReminder:
        queue_metadata = {
            **queue_metadata,
            'reminder': notification,
        }
    else:
        queue_metadata = {
            **queue_metadata,
            'notification': notification,
        }
    variables = {
        'queueName': queue['name'],
        # * get all notification params
        'metadata': json.dumps(queue_metadata),
    }
    response, errors = gql.mutate(mutations.update_queue_meta, variables)
    if errors:
        log(LogLevel.ERROR, 'Error saving smart notification data (to Queue):')
        log(LogLevel.ERROR, errors)
        return


def notification(content):
    """This function makes a simple notification,

    Args:
        content (dict): Variables that complete the message of the notification

    Returns:
        GraphqlResponse: Returns a GraphqlResponse, a succesful message.
    """
    response, errors = gql.mutate(
        mutations.create_notification, variables=content)
    return response, errors


def groupNotification(
    groupName,
    content=None,  # dictionary containing the static information to display in the Notification
    # TODO: function that gets the user info as input and returns the content as output
    contentBuilder=None
):
    """This function makes a simple notification to a group of "users". 

    Args:
        groupName (str): Group's name
        content (dict, optional): Variables that complete the message of the 
          notification. Defaults to None.

    Returns:
        dict: Returns a succesful message.
    """
    # ! get groups information
    groupUsers, errors = gql.query(queries.get_group_users, variables={
                                   'groupName': groupName})
    if errors:
        return {'successful': False, 'errors': errors}
    if len(groupUsers) == 0:
        return {'successful': False, 'errors': ['No group users for the selected group.']}
    # ! if group exists, send notifications for the entire group:
    all_errors = []
    for groupUser in groupUsers:
        userId = pydash.get(groupUser, 'user.id')
        _, errors = gql.mutate(
            mutations.create_notification,
            variables={
                **content,
                # Attaches the user information to the content of the notification
                'userId': int(userId)
            }
        )
        all_errors.extend(errors)
    # ! if something wrong, inform the error(s) to the caller function:
    if all_errors:
        return {'successful': False, 'errors': all_errors}
    # ! if everything ok, notify the caller function the OK output:
    else:
        return {'successful': True, 'errors': []}
