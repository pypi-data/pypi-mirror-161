from processrepo.ProcessRunProfile import ProcessRunProfile


def serialize_process_run_profile(process_run_profile: ProcessRunProfile) -> dict:
    serialized = {
        'market': process_run_profile.market,
        'name': process_run_profile.name,
        'run_profile': process_run_profile.run_profile.value,
        'enabled': process_run_profile.enabled
    }
    return serialized
