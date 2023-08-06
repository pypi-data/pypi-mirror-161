from apscheduler.util import undefined
from apscheduler.events import EVENT_ALL
from tornado.options import options


class TaskHelper:
    @staticmethod
    def add_job(func, trigger=None, args=None, kwargs=None, id=None, name=None,
                misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                next_run_time=undefined, jobstore='default', executor='default',
                replace_existing=False, **trigger_args):
        job = options.scheduler.add_job(func, trigger=trigger, args=args, kwargs=kwargs, id=id, name=name,
                                        misfire_grace_time=misfire_grace_time, coalesce=coalesce,
                                        max_instances=max_instances,
                                        next_run_time=next_run_time, jobstore=jobstore, executor=executor,
                                        replace_existing=replace_existing, **trigger_args)
        return job

    @staticmethod
    def scheduled_job(trigger, args=None, kwargs=None, id=None, name=None,
                      misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined,
                      next_run_time=undefined, jobstore='default', executor='default',
                      **trigger_args):
        inner = options.scheduler.scheduled_job(trigger, args=args, kwargs=kwargs, id=id, name=name,
                                                misfire_grace_time=misfire_grace_time, coalesce=coalesce,
                                                max_instances=max_instances,
                                                next_run_time=next_run_time, jobstore=jobstore, executor=executor,
                                                **trigger_args)
        return inner

    @staticmethod
    def modify_job(job_id, jobstore=None, **changes):
        job = options.scheduler.modify_job(job_id, jobstore=jobstore, **changes)
        return job

    @staticmethod
    def reschedule_job(job_id, jobstore=None, trigger=None, **trigger_args):
        job = options.scheduler.reschedule_job(job_id, jobstore=jobstore, trigger=trigger, **trigger_args)
        return job

    @staticmethod
    def pause_job(job_id, jobstore=None):
        job = options.scheduler.pause_job(job_id, jobstore=jobstore)
        return job

    @staticmethod
    def resume_job(job_id, jobstore=None):
        job = options.scheduler.resume_job(job_id, jobstore=jobstore)
        return job

    @staticmethod
    def get_jobs(jobstore=None, pending=None):
        jobs = options.scheduler.get_jobs(jobstore=jobstore, pending=pending)
        return jobs

    @staticmethod
    def get_job(job_id, jobstore=None):
        job = options.scheduler.get_job(job_id, jobstore=jobstore)
        return job

    @staticmethod
    def remove_job(job_id, jobstore=None):
        options.scheduler.remove_job(job_id, jobstore=jobstore)

    @staticmethod
    def remove_all_jobs(jobstore=None):
        options.scheduler.remove_all_jobs(jobstore=jobstore)

    @staticmethod
    def print_jobs(jobstore=None, out=None):
        options.scheduler.print_jobs(jobstore=jobstore, out=out)

    @staticmethod
    def add_executor(executor, alias='default', **executor_opts):
        options.scheduler.add_executor(executor, alias=alias, **executor_opts)

    @staticmethod
    def remove_executor(alias, shutdown=True):
        options.scheduler.remove_executor(alias=alias, shutdown=shutdown)

    @staticmethod
    def add_jobstore(jobstore, alias='default', **jobstore_opts):
        options.scheduler.add_jobstore(jobstore, alias=alias, **jobstore_opts)

    @staticmethod
    def remove_jobstore(alias, shutdown=True):
        options.scheduler.remove_jobstore(alias=alias, shutdown=shutdown)

    @staticmethod
    def add_listener(callback, mask=EVENT_ALL):
        options.scheduler.add_listener(callback, mask=mask)

    @staticmethod
    def remove_listener(callback):
        options.scheduler.remove_listener(callback)
