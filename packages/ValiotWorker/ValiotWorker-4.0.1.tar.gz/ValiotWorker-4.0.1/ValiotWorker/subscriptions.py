
JOB_CREATED = '''
subscription  JobCreated(
  $workerCode: String!
){
  jobCreated(filter: { workerCode: $workerCode }){
    successful
    messages{field message}
    result{
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
        enabled
        context # for rehydration
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
      worker{
        id
        code
        name
      }
    }
  }
}
'''

JOB_UPDATED = '''
subscription {
  jobUpdated{
    successful
    messages{
      field
      message
    }
    result{
      id
      jobStatus
    }
  }
}
'''