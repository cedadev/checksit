"""
checksit check /badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/01/rss/day/latest/rss_rcp85_land-cpm_uk_2.2km_01_day_20671201-20681130.nc

checksit check --verbose /group_workspaces/jasmin2/ukcp18/UKcordex-laura/tasmax_rcp85_land-rcm_uk_12km_EC-EARTH_r12i1p1_HIRHAM5_day_19801201-19901130.nc

checksit check /badc/ukcp09/data/gridded-land-obs/gridded-land-obs-monthly/grid/ascii/rainfall/2016/ukcp09_gridded-land-obs-monthly_5km_rainfall_201610.txt

checksit check  /badc/ukmo-assim/data/standard/2022/ukmo-nwp-strat_gbl-std_2022020112_u-v-gph-t-w.pp

checksit check -m cltAnom=cloud_area_fraction /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc

# Vocabs checked as well
checksit check -m cltAnom=cloud_area_fraction /gws/nopw/j04/cmip6_prep_vol1/ukcp18/data/land-prob/v20211110/uk/25km/rcp85/sample/b8110/30y/cltAnom/mon/v20211110/cltAnom_rcp85_land-prob_uk_25km_sample_b8110_30y_mon_20091201-20991130.nc

"""

import os
import time
import datetime as dt

from wflogger.credentials import user_id, hostname, creds
from wflogger.wflogger import INSERT_SQL

v_1 = {"workflow": "my-model-1",
       "tag": "idl-version",
       "stages": [(1, "start", 0), (2, "read", 3), (3, "process", 10), (4, "summarise", 4)],
       "n_iterations": 200}

v_2 = {"workflow": "my-model-1",
       "tag": "python-version",
       "stages": [(1, "start", 0), (2, "read", 8), (3, "process", 12), (4, "summarise", 2)],
       "n_iterations": 300}

host_tmpl = "host{n:03d}.jc.rl.ac.uk"
BAD_HOSTS = [host_tmpl.format(n=n) for n in range(101, 130)]


def _random_duration(n):
    # Add some randomness
    if randint(0, 1000) > 995:
        return randint(44, 75)

    secs = randint(-20, 40) * 0.1 + n
    if secs < 0: secs = 0.01
    return secs
    

def SLOW_test_load_workflows_simulating_realtime_interactions():
    for wf in (v_1, v_2):
        max_iter = wf["n_iterations"] + 1

        for iteration in range(1, max_iter):
            for stage_number, stage, wait in wf["stages"]:
                secs = _random_duration(wait)
                time.sleep(secs)
                insert_record(wf["workflow"], wf["tag"], stage_number, stage, iteration)
 

def _get_random_host():
    n = randint(70, 700)
    return host_tmpl.format(n=n)


def test_load_workflows_faking_date_times():

    date_time = dt.datetime.now()

    conn = psycopg2.connect(creds)
    curs = conn.cursor()

    for wf in (v_1, v_2):
        max_iter = wf["n_iterations"] + 1

        for iteration in range(1, max_iter):

            hostname = _get_random_host()
            
            for stage_number, stage, wait in wf["stages"]:

                secs = _random_duration(wait)
                if hostname in BAD_HOSTS:
                    secs += 100

                date_time += dt.timedelta(seconds=secs)

                workflow, tag = wf["workflow"], wf["tag"]
                comment, flag = "", -999
                curs.execute(INSERT_SQL, 
                    (user_id, hostname, workflow, tag, stage_number,
                     stage, iteration, date_time, comment, flag))

    conn.commit()
    curs.close()
    conn.close() 

