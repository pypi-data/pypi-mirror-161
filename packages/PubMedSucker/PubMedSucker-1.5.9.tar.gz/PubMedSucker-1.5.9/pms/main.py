"""PubMedsucker - PMS

https://git.connect.dzd-ev.de/dzdtools/pubmedsucker

Copyright 2020 Deutsches Zentrum für Diabetesforschung e.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


# TODO
# * handle PubmedBookArticleSet


import os
import sys
import logging
import graphio
import py2neo
from linetimer import CodeTimer
from DZDutils.neo4j import wait_for_db_boot
from Configs import getConfig


def run():
    from pms.tools import create_config_dirs, get_phase1_file_list, get_graph
    import pms
    from pms.config import DEFAULT

    config: DEFAULT = getConfig()
    create_config_dirs()

    from pms.final_transforming import delete_old_articles, run_transforming_queries
    from pms.import_worker.worker import Worker
    import neobulkmp
    from getversion import get_module_version

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
        handlers=[logging.StreamHandler((sys.stdout))],
    )

    log = logging.getLogger("PubmedSuckerManagerProcess")
    log.addHandler(logging.FileHandler(config.MANAGER_LOGFILE, mode="a"))

    statistic_logger = logging.getLogger("PMSStatistics")
    statistic_logger.addHandler(logging.FileHandler(config.STATISTICS_LOGFILE))

    log.info(f"Pubmedsucker version: '{get_module_version(pms)[0]}'")
    log.info(f"\t neobulkmp version: '{get_module_version(neobulkmp)[0]}'")
    log.info(f"\t py2neo version: '{get_module_version(py2neo)[0]}'")
    log.info(f"\t graphio version: '{get_module_version(graphio)[0]}'")

    log.info(f"config.NEO4J {type(config.NEO4J)}: {config.NEO4J}")
    log.info(f"config.REDIS {type(config.REDIS)}: {config.REDIS}")
    log.info("PUBMED_SOURCE: {}".format(config.PUBMED_SOURCE))
    wait_for_db_boot(config.NEO4J, timeout_sec=60, log_func=log.info)
    try:
        article_count_at_start = (
            get_graph()
            .begin()
            .run("MATCH (a:PubMedArticle) return count(a) as cnt")
            .data()[0]["cnt"]
        )
    except Exception as e:
        log.error(
            "Error: Can not reach neo4j DB '{}'. Aborting import...".format(
                config.NEO4J
            )
        )
        raise
    article_deleted_count = 0
    timer = CodeTimer("CompleteProcessTimer", unit="s", silent=True)

    with timer:
        p1timer = CodeTimer("Phase1ProcessTimer", unit="s", silent=True)
        with p1timer:
            # Start PHASE 1 - Loading Phase
            log.info("#--------START LOADING PHASE  (1/2)---------#")
            worker_manager = neobulkmp.Manager(
                worker_sourcing_class=Worker,
                worker_parameters=get_phase1_file_list(),
                cache_backend_params=config.REDIS,
                debug=config.DEBUG,
            )
            if isinstance(config.STATUS_LOG_INTERVAL_SEC, str):
                from py_expression_eval import Parser
                # parse expressions like "60*6"
                worker_manager.status_log_every_n_sec = int(Parser().parse(config.STATUS_LOG_INTERVAL_SEC).evaluate({}))
            else:
                worker_manager.status_log_every_n_sec = int(config.STATUS_LOG_INTERVAL_SEC)
            try:
                worker_manager.cache.test_connection()
            except Exception as e:
                log.error(f"Redis not available:\n {type(e).__name__}: {str(e)}")
                exit(1)
            worker_manager.strategy.max_processes_count = config.MAX_WORKER_COUNT
            worker_manager.strategy.max_graphobjects_count_in_cache = (
                config.MAX_NODES_N_RELS_IN_CACHE_BEFORE_PAUSING_PARSING
            )
            worker_manager.worker_loading_class.amount_of_retries_on_loading_fail = (
                config.MAX_RETRIES_ON_INSERT_ERRORS
            )
            worker_manager.strategy._last_amount_sourcing_cores = (
                config.MIN_PARSING_WORKERS_COUNT
            )
            worker_manager.report_statistics_print_func = statistic_logger.info
            worker_manager.strategy.graphio_batchsize = config.GRAPHIO_BATCHSIZE
            worker_manager.worker_log_level = config.LOG_LEVEL
            worker_manager.create_indexes = True
            worker_manager.merge(graph_params=config.NEO4J)
            # END OF PHASE 1

            # Start PHASE 2 - polishing transforming, delete old data and artefacts
        p2timer = CodeTimer("Phase3ProcessTimer", unit="s", silent=True)
        article_count_before_deletion = (
            get_graph()
            .begin()
            .run("MATCH (a:PubMedArticle) return count(a) as cnt")
            .data()[0]["cnt"]
        )
        with p2timer:
            log.info("#--------START TRANSFORMING PHASE (2/2)---------#")
            article_deleted_count = delete_old_articles()
            run_transforming_queries()

    article_count_after = (
        get_graph()
        .begin()
        .run("MATCH (a:PubMedArticle) return count(a) as cnt")
        .data()[0]["cnt"]
    )

    log.info(
        f"Inserted {article_count_before_deletion - article_count_at_start} Articles in {int(timer.took / 60)} Minutes and {int(timer.took % 60)} Seconds. Deleted {article_deleted_count} Articles. Resulting article count in total: {article_count_after}.")

    log.info(
        " Phase 1 loading took {} Minutes and {} Seconds. thats {}% of the total time".format(
            int(p1timer.took / 60),
            int(p1timer.took % 60),
            round((p1timer.took / timer.took) * 100, 4),
        )
    )

    log.info(
        " Phase 2 loading took {} Minutes and {} Seconds. thats {}% of the total time".format(
            int(p2timer.took / 60),
            int(p2timer.took % 60),
            round((p2timer.took / timer.took) * 100, 4),
        )
    )

    # rancher forced autorestart dirty quickfix
    if not config.EXIT_WHEN_DONE:
        import time

        while True:
            time.sleep(60)


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.append(os.path.normpath(SCRIPT_DIR))
    run()
