import numpy as np
import uproot

def cherrypicking(file_path, user_event_id, output_path):
    """
    Sometimes a raw_data file may contain many events we are not interested
    in. This function reduce the file size by selecting the entries
    of interest. Each entry is uniquely defined by event_id. User 
    need to provide a list of desired event_id. This function will 
    create a new smaller file, and same the entries of interest only.
    All branch types stay the same.

    Args:
        file_path: str
        user_event_id: list of int
        output_path: str
    """
    daq_path = file_path+':daq'
    run_path = file_path+':run_info'
    t_old = uproot.open(daq_path)
    a_old = t_old.arrays(library='np')
    n_entries=len(a_old['event_id'])
    mask = np.full(n_entries, False)
    for i in range(n_entries):
        this_id = a['event_id'][i]
        if this_id in user_event_id:
            mask[i]=True
    a_new = {}
    for k in a.keys():
        a_new[k]=a[k][mask]
    f_new = uproot.recreate("small.root")
    t_run = uproot.open(run_path)
    f_new['run_info'] = t_run.arrays(library='np')
    f_new['daq']=a_new
    f_new.close()
    print('Info: cherry-picked events are saved to', output_path)
