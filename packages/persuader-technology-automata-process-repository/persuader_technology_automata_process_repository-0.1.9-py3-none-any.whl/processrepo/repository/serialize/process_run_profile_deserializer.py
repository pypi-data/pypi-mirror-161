from coreutility.collection.dictionary_utility import as_data

from processrepo.ProcessRunProfile import ProcessRunProfile, RunProfile


def deserialize_process_run_profile(process_run_profile, market, name) -> ProcessRunProfile:
    if process_run_profile is not None:
        run_profile = RunProfile.parse(as_data(process_run_profile, 'run_profile'))
        enabled = as_data(process_run_profile, 'enabled')
        return ProcessRunProfile(market, name, run_profile, enabled)
