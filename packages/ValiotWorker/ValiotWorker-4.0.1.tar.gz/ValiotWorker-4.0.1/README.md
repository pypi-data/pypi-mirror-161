# python-gql-worker
Enables running Python functions as standalone jobs based on interaction with valiot-jobs API

# installation
`pipenv install valiotworker`

# Deployment:
`python setup.py sdist bdist_wheel && python -m twine upload dist/* --skip-existing # UPLOAD TO PYPI`

## API < v0.4.0
Job footprint:

```
@valiotWorker.job(...)
def my_job(job_id, update_job, kwargs)
  ...
```
Parameters:
* job_id: Number representing the Identifier for this job
* update_job: function to update status of current job (FINISHED, ERROR, etc)
* kwargs: dictionary aliasing the custom params (from job's "input" attribute, for retrocompatibility)

## API >= v0.5.0
```
@valiotWorker.job(...)
def my_job(my_arg1, my_arg2, ... my_arg_n, **_)
  ...
```

Starting from v0.5.0, every argument is accessed by its keyword.

You may have any arbitrary number of arguments which get loaded from the job **input** parameter, and the special arguments:
* update_job: function to update status of current job (FINISHED, ERROR, etc)
* job: dictionary containing job information (id, status, queue, insertion date, etc)
* queue: dictionary containing Job's parent Queue information (name, type, frequency, etc)
* kwargs: dictionary aliasing the custom params (from job's "input" attribute, for retrocompatibility)

### Worker configuration:
This configurations must run before `worker.run()` (event loop)
```python
# Poll with subscription
worker.setPollingMode(PollingMode.SUBSCRIPTION)
# or Poll with Queries
worker.setPollingMode(PollingMode.QUERY)
```
worker.setJobConfigMode(JobConfigMode.KEEP)
```python
# Config remains untouched (Allow persistence of config on DB)
worker.setJobConfigMode(JobConfigMode.KEEP)
# Config updates with job params (Allow quick iteration of job setups)
worker.setJobConfigMode(JobConfigMode.SYNC)
```