create_job = '''
  mutation createJob(
    $queueName: String!
    $worker: String
  ){
    createJob(
      queueName: $queueName
      workerCode: $worker
      jobStatus: WAITING
      progress: 0
      input: "{}"
      output: "{}"
    ){
      successful
      messages{
        message
        field
      }
      result{
        id
        input
        output
        jobStatus
        progress
        queue{
          id
          name
          updatedAt
        }
      }
    }
  }
'''

update_job = '''
  mutation UpdateJob(
    $id: ID!
    $status: JobStatus!
    $output: Jsonb
    $progress: Int
  ) {
    updateJob(
      id: $id
      job: {
        jobStatus: $status
        progress: $progress
        output: $output
      }
    ) {
      successful
      result {
        id
      }
      messages {
        message
      }
    }
  }
'''

delete_job = '''
  mutation abortJob($id: ID!) {
    updateJob(id: $id job: { jobStatus: ABORTED }) {
      successful
      messages{
        field
        message
      }
      result{
        id
      }
    }
  }
'''

upsert_queue = '''
mutation upsertQueue(
  $name: String!
  $alias: String!
  $type: QueueType!
  $enabled: Boolean
  $description: Text
  $schedule: String
  $query: Text
  $lockRequired: Boolean
) {
  upsertQueue(
    name: $name
    queue: {
      alias: $alias
      type: $type
      enabled: $enabled
      description: $description
      schedule: $schedule
      query: $query
      lockRequired: $lockRequired
    }
  ) {
    successful
    result {
      id
      name
      alias
      type
      description
      schedule
      enabled
      query
      lockRequired
    }
    messages {
      message
      field
    }
  }
}
'''

run_job = '''
  mutation runJob(
    $id: ID!
    $status: JobStatus!
    $queueName: String!, 
    $lastRunAt: DateTime!
  ) {
    updateJob(
      id: $id
      job: {
        jobStatus: $status
        progress: 0
        output: "{}"
        }
    ) {
      successful
      messages { field message }
      result { id jobStatus progress }
    }
    updateQueue(
      findBy: { name: $queueName },
      queue: { lastRunAt: $lastRunAt }
    ) {
      successful
      messages { field message }
      result { id name lastRunAt }
    }
  }
'''

run_event_job = '''
  mutation runJob($queueName: String!, $lastRunAt: DateTime!) {
  job: createJob(
    queueName: $queueName
    jobStatus: RUNNING
    progress: 0
    output: "{}"
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
      jobStatus
      progress
    }
  }
  queue: updateQueue(
    findBy: { name: $queueName }
    queue: { lastRunAt: $lastRunAt }
  ) {
    successful
    messages {
      field
      message
    }
    result {
      id
      name
      lastRunAt
    }
  }
}
'''

create_notification = '''
mutation CreateNotification(
  $userId: ID
  $context: NotificationType,
  $title: String,
  $content: Text,
  $link: String,
  $metadata: String,
  $linkText: String
){
  createNotification(
    read: false
    userId: $userId
    context: $context
    title: $title
    content: $content
    link: $link
    linkText: $linkText
    metadata: $metadata
  ){
    successful
    result{
      id
      title
      content
      context
      metadata
      insertedAt
      updatedAt
    }
    messages{
      message
    }
  }
}
'''

'''
Queue metadata:
{
  "reminder": {
    "id": "123"
    "SentAt": "2019-07-26T12:51:16Z",
    # ! The reminder is sent without a RESOLVED prop
    "enabled": true,
  },
  "notification": {
    "id": "121"
    "title": "blabla",
    "content": "this is notification",
    "context": "DANGER",
    "metadata": "..." # ! If this function is used to create notifications, we assume a "resolved: false" must be sent with it
  }
}
'''
update_queue_meta = '''
  mutation updateQueueMetadata(
    $queueName: String!
    $metadata: Text!
  ){
    updateQueue(
      findBy:{name: $queueName}
      queue:{
        query: $metadata
      }
    ){
      successful
      messages{
        message
        field
      }
      result{
        id
        name
        alias
        description
        enabled
        schedule
        query
      }
    }
  }
'''

update_notification_metadata = '''
  mutation updateMetadata(
    $id: ID!
    $metadata: String!
  ){
    updateNotification(
      id:$id
      notification:{
        metadata: $metadata
      }
    ){
      successful
      messages{
        field
        message
      }
      result{
        id
        read
        title
        content
        context
        metadata
        insertedAt
        updatedAt
      }
    }
  }
'''

create_lock = '''
mutation createLock(
  $worker: String!
  $queue: String!
  $startAt: DateTime
){
  createQueueLock(
    active: true
    workerCode: $worker
    queueName: $queue
    startAt: $startAt
  ){
    successful
    messages{
      field
      message
    }
    result{
      id
      active
      startAt
      endAt
      insertedAt
      worker{id code}
      queue{id name}
    }
  }
}
'''

update_lock = '''
mutation UpdateLock($id: ID!, $active: Boolean!, $endAt: DateTime) {
  updateQueueLock(id: $id, queueLock: { active: $active, endAt: $endAt }) {
    successful
    messages {
      field
      message
    }
    result {
      id
      active
      startAt
      endAt
      insertedAt
      worker {
        id
        code
      }
      queue {
        id
        name
      }
    }
  }
}
'''

update_context = '''
mutation UpdateContext(
  $queue: String!
  $context: Jsonb!
){
  updateQueue(
    findBy:{ name: $queue }
    queue: {
      context: $context
    }
  ){
    successful
    messages{
      field
      message
    }
    result{
      id
      name
      context
    }
  }
}
'''

create_queue_worker = '''
  mutation (
    $worker: String!
    $queue: String!
    $enabled: Boolean!
  ){
    createQueueWorker(
      workerCode: $worker
      queueName: $queue
      enabled: $enabled
    ) {
      successful
      messages {
        field
        message
      }
    }
  }
'''

update_queue_worker = '''
  mutation (
    $id: ID!
    $enabled: Boolean!
  ){
    updateQueueWorker(
      id: $id
      queueWorker: {
        enabled: $enabled
      }
    ) {
      successful
      messages {
        field
        message
      }
    }
  }
'''


def build_batch_stale_mutation(jobs):
    batch_template = '''mutation DeleteStaleJobs{{\n\t{mutation_items}\n}}'''
    item_template = '''{label}: updateJob(id: {id} job: {{ jobStatus: ABORTED }}) {{ successful messages{{field message}} }}'''
    mutation_items = [
        item_template.format(label=f'delete_job_{job["id"]}', id=job["id"])
        for job in jobs
    ]
    return (
        batch_template.format(mutation_items='\n\t'.join(mutation_items))
        if jobs
        else None
    )
