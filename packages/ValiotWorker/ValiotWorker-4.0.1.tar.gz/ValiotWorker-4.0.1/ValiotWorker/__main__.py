import os
from pprint import pprint
from pygqlc import GraphQLClient
from .worker import ValiotWorker
from .worker import QueueType
# ! Create main helpers:
gql = GraphQLClient()
vw = ValiotWorker()
# * Initialize helpers:
gql.addEnvironment(
    'dev',
    url=os.environ.get('API'),
    wss=os.environ.get('WSS'),
    headers={'Authorization': os.environ.get('TOKEN')},
    default=True)
vw.setClient(gql)
vw.setWorker(os.environ.get('WORKER'))


@vw.job(
    name='TEST_JOB',
    alias='test job 1',
    description='',
    schedule='* * * * *',
    enabled=True,
    queueType=QueueType.FREQUENCY,
)
def test_job(job_id, update_job, kwargs):
    print("Hi, I'm test job #1")
    update_job({
        'id': job_id,
        'status': 'FINISHED',
        'output': '{}',
        'progress': 100
    })


@vw.job(
    name='TEST_JOB_2',
    alias='test job 2',
    description='',
    schedule='*/3 * * * *',
    enabled=True,
    queueType=QueueType.FREQUENCY,
)
def test_job_2(job_id, update_job, kwargs):
    print("Hi, I'm test job #2")
    update_job({
        'id': job_id,
        'status': 'FINISHED',
        'output': '{}',
        'progress': 100
    })


def main():
    print('main for valiot worker')
    vw.run()


if __name__ == "__main__":
    main()
