import time
from types import SimpleNamespace

from elementary_flask.globals import current_elementary_flask_app as _app
from elementary_flask.typing import Iterable, CronEntry
from elementary_flask.helpers.redis import pottery_factory

NEXT_JOBS_KEY = 'ELEMENTARY_FLASK_CORE_CRON_JOBS'
SCHEDULED_JOBS_KEY = 'ELEMENTARY_FLASK_CORE_CRON_SCHEDULED'
# ENTRIES_KEY = 'ELEMENTARY_FLASK_CORE_CRON_ENTRIES'
# # ENTRY_KEY_PREFIX = 'ELEMENTARY_FLASK_CORE_CRON_ENTRY_'
CRON_LOCK_KEY = 'ELEMENTARY_FLASK_CORE_CRON_LOCK'
SCHEDULED_CACHE_TIMEOUT = 86400  # 24h
_next_jobs = None
_cron_lock = None


def _get_next_jobs():
    global _next_jobs
    if _next_jobs is None:
        _next_jobs = pottery_factory.RedisDict(key=NEXT_JOBS_KEY)
    return _next_jobs


def _get_lock():
    global _cron_lock
    if _cron_lock is None:
        _cron_lock = pottery_factory.Redlock(key=CRON_LOCK_KEY)
    return _cron_lock


def _get_cache_dict(key):
    return pottery_factory.RedisDict(key=key)


# def cron_endpoint(crontab: Iterable[CronEntry] = None, current_time: int = None):
#     crontab = crontab if crontab is not None else _app.crontab
#     fail, success = 0, 0
#
#     def _fire(cn, st):
#         nonlocal fail, success
#         try:
#             cron_entry.fire(SimpleNamespace(cron_name=cn, scheduled_time=st, current_time=current_time))
#             success += 1
#             return True
#         except Exception:
#             _app.logger.warning('Error executing cron: %s', cron_name, exc_info=True)
#             fail += 1
#             return False
#         finally:
#             _get_next_jobs().pop(cron_name, None)
#             _get_next_jobs()[cron_name] = current_time, st, True
#
#     def _check_current():
#         if nxt == current_time:
#             _fire(cron_name, nxt)
#         else:
#             _get_next_jobs()[cron_name] = current_time, nxt, False
#
#     def _check_cached_job():
#         if cron_name in _get_next_jobs():
#             cache_ct, cache_nxt, cache_fired = _get_next_jobs()[cron_name]
#             # check cache_ct is correct and entry cron config has not been updated; otherwise ignore cache
#             if cache_ct < current_time and int(cron_entry.get_next(cache_ct - 1)) == cache_nxt:
#                 if cache_nxt <= current_time and not cache_fired:
#                     _fire(cron_name, cache_nxt)
#                     if cache_nxt != nxt:
#                         _check_current()
#                     return True
#         return False
#
#     with _get_lock():
#         current_time = current_time if current_time is not None else (int(time.time()) // 60) * 60
#         for cron_entry in crontab:
#             cron_name = cron_entry.name
#             nxt = int(cron_entry.get_next(current_time - 1))
#
#             if not _check_cached_job():
#                 _check_current()
#
#         next_jobs_len = len(_get_next_jobs())
#         _app.logger.debug('Cron queue contains %d item: %s', next_jobs_len,
#                           tuple(f'{k}: {str(datetime.fromtimestamp(v))}' for k, v in _get_next_jobs().items()))
#
#     return {'failed_tasks': fail, 'successful_tasks': success, 'total_run_tasks': fail + success,
#             'tasks_waiting': next_jobs_len}

def cron_endpoint(crontab: Iterable[CronEntry] = None, current_time: int = None):
    crontab = crontab if crontab is not None else _app.crontab
    fail, success = 0, 0

    def _fire(st):
        nonlocal fail, success, fired
        try:
            cron_entry.fire(SimpleNamespace(cron_name=cron_name, scheduled_time=st, current_time=current_time))
            success += 1
            return True
        except Exception:
            _app.logger.warning('Error executing cron: %s', cron_name, exc_info=True)
            fail += 1
            return False
        finally:
            fired = True
            next_jobs.pop(cron_name, None)
            done_jobs[_scheduled_key(st)] = current_time

    def _scheduled_key(st):
        return f"{cron_name}-{st}"

    def _check_done_jobs(st):
        scheduled_key = _scheduled_key(st)
        return scheduled_key not in done_jobs or not done_jobs[scheduled_key]

    with _get_lock():
        current_time = current_time if current_time is not None else (int(time.time()) // 60) * 60
        next_jobs = _get_next_jobs()
        done_jobs = _get_cache_dict(SCHEDULED_JOBS_KEY)

        # Debug info
        _app.logger.debug('Cron Next Jobs: %r', next_jobs)
        _app.logger.debug('Cron Done Jobs: %s', done_jobs)

        for cron_entry in crontab:
            cron_name = cron_entry.name
            nxt = cron_entry.get_next_ex1(current_time)
            fired = False

            if nxt == current_time:
                if _check_done_jobs(nxt):
                    _fire(nxt)

            if not fired and cron_name in next_jobs:
                nj_ct, nj_st = next_jobs[cron_name]

                # scheduled time passed and cron entry has not been updated
                if current_time >= nj_st == cron_entry.get_next_ex1(nj_ct) and _check_done_jobs(nj_st):
                    _fire(nj_st)

            if not fired:
                next_jobs[cron_name] = current_time, nxt

        next_jobs_len = len(next_jobs)
        # Debug info
        _app.logger.debug('Cron Next Jobs: %r', next_jobs)
        _app.logger.debug('Cron Done Jobs: %s', done_jobs)

        # clean scheduled cache
        to_delete = list()
        for k, ct in done_jobs.items():
            if current_time - ct > SCHEDULED_CACHE_TIMEOUT:
                to_delete.append(k)

        for k in to_delete:
            done_jobs.pop(k, None)

    return {'failed_tasks': fail, 'successful_tasks': success, 'total_run_tasks': fail + success,
            'tasks_waiting': next_jobs_len}
