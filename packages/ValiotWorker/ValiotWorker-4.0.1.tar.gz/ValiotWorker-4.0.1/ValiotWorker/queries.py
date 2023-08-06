get_worker='''
query GetWorker($code: String!){
  worker(findBy:{ code: $code}){
    id
    code
    name
    jobs(orderBy:{ desc: ID } limit: 1){
      id
    }
  }
}
'''

all_jobs='''
query WorkerJobs($worker: String){
    jobs(
        orderBy: { asc: ID }, 
        filter: {
          jobStatus: WAITING
          workerCode: $worker
        }
    ) {
        id
        userId
        input
        context
        output
        progress
        jobStatus
        queue {
          id
          name
          alias
          type
          context # for rehydration
          enabled
          schedule
          query
          lockRequired
          # locks(orderBy:{desc:ID} limit: 1){
            # id
            # active
            # startAt
            # endAt
          # }
        }
    }
}
'''

waiting_jobs = '''
query WorkerWaitingJobs($worker: String){
  jobs(filter: {
    workerCode: $worker
    jobStatus: WAITING
  }) {
    id
  }
}
'''

paginate_stale_jobs = '''
  query WorkerWaitingJobsPaginate(
    $worker: String!
    $cursor: Int = 0
    $limit: Int = 10
  ){
    jobsPaginate(
      cursor: $cursor
      filter: {
        workerCode: $worker
        jobStatus: WAITING
      }
      orderBy: {asc: ID}
      limit: $limit
    ) {
      pageInfo { endCursor hasNextPage }
      jobs: edge{ id }
    }
  }
'''

get_job ='''
query GetJob(
  $id: ID!
){
    job(
        id: $id
    ) {
        id
        input
        output
        jobStatus
        queue {
          id
          name
          alias
          type
          enabled
          schedule
          query
        }
    }
}
'''

get_queue = '''
query QueueByName(
  $queueName: String
)
{
  queue(
    findBy:
    {name: $queueName}
  ){
    id
    name
    alias
    type
    enabled
    schedule
    query
  }
}
'''

all_queues_w_listeners = '''
{
  queues{
    id
    name
    alias
    description
    context
    type
    schedule
    query
    lastRunAt
    lockRequired
    jobs(orderBy: { desc:ID } limit: 1){
      id
      updatedAt
    }
    locks(orderBy:{ desc:ID } limit: 1){
      id
      active
      startAt
      endAt
    }
    listeners: queueWorkers {
      id
      enabled
      worker{
        id
        code
      }
    }
    updatedAt
    insertedAt
  }
}
'''

get_queue_last_jobs = '''
query QueueLastJobs(
  $name: String!
  $count: Int!
  $worker: String
){
  queue(
    findBy: {
      name:$name
    }
  ){
    id
    name
    alias
    enabled
    jobs(
      filter:{workerCode: $worker}
      orderBy:
      {desc: INSERTED_AT}
      limit: $count
    ){
      id
      jobStatus
      output
    }
  }
}
'''

get_queue_last_job = '''
query QueueLastJob(
  $name: String!
  $worker: String
){
  queue(
    findBy: {
      name:$name
    }
  ){
    id
    name
    alias
    enabled
    jobs(
      filter:{workerCode: $worker}
      orderBy:
      {desc: INSERTED_AT}
      limit: 1
    ){
      id
      jobStatus
      output
    }
  }
}
'''

get_notification = '''
  query getNotification($id: ID!){
    notification(id: $id){
      id
      title
      content
      context
      read
      metadata
      insertedAt
    }
  }
'''

get_group_users = '''
  query GetGroupUsers ($groupName: String!){
    groupUsers(filter: { groupName: $groupName }) {
      id
      group {
        id
        name
      }
      user {
        id
        name
        lastName
        email
        signInCount
        previousSignIp
        currentSignInIp
        previousSignInAt
        currentSignInAt
        insertedAt
      }
    }
  }
'''

get_worker_queues = '''
  query WorkerQueues($workerCode: String!){
    queueWorkers(filter: {workerCode: $workerCode}){
      id
      worker{
        id
        code
      }
      queue{
        id
        name
      }
      enabled
    }
  }
'''

get_queueLocks = '''
query($workerCode:String, $queueName:String){
  queueLocks(orderBy:{desc:ID}, filter:{workerCode:$workerCode, queueName:$queueName , active:true}){
    id
    active
  }
}'''