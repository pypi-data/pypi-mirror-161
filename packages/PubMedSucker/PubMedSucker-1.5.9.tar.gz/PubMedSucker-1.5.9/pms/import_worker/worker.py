import os
import time
import json
import urllib
from Configs import getConfig
from linetimer import CodeTimer
import logging
from logging import Logger
import sys
from getversion import get_module_version

from neobulkmp import WorkerSourcing
from pms.import_worker.parser import PubMedXMLParser
from pms.import_worker.pubmed_source_file_handler import PubMedSourceFileHandler
from py2neo import Node, Graph
import pms

config = getConfig()

logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)-15s %(processName)-8s %(module)-8s %(levelname)-8s:  %(message)s",
    handlers=[logging.StreamHandler((sys.stdout))],
)


class Worker(WorkerSourcing):
    log: Logger = None

    def run(self):
        self.cache = self.cache_backend(self.cache_backend_params)
        self.log: logging.Logger = self.get_logger()
        self.log.addHandler(logging.FileHandler(config.WORKER_LOGFILE))
        self.graph = Graph(**config.NEO4J)
        self.source_file_handler = PubMedSourceFileHandler(
            self.worker_parameter["xml_url"]
        )
        if (
            self._fetch_loading_log() is not None
            and not config.FORCE_REMERGING_LOADED_PUBMED_XMLS
        ):
            self.log.info(
                "Skip '{}' . File was allready parsed and loaded into DB. ...".format(
                    self.source_file_handler.get_target_filename()
                )
            )
            return
        self.log.info(f"Start processing {self.worker_parameter['xml_url']} gogogoooo!")
        self.parser = PubMedXMLParser(
            parent_worker=self, xml_file_handler=self.source_file_handler
        )

        self.parser.run(self.cache)
        self._create_loading_log()

    def _create_node(self, labels: "list(str)", props: dict):
        # this is a little helper function to create some log,metadata nodes
        tx = self.graph.begin()
        tx.create(Node(*labels, **props))
        tx.commit()

    def _create_loading_log(self):
        self._create_node(
            config.LOADING_LOG_LABELS,
            {
                "filename": self.source_file_handler.get_target_filename(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S %z"),
                "PubMedSucker_Version": get_module_version(pms)[0],
                "article_deletions_count": len(self.parser.delete_pmids),
                "to_be_deleted_articles": self.parser.delete_pmids,
            },
        )

    def _fetch_loading_log(self):
        query = "MATCH (n:{}) WHERE n.filename='{}' return n".format(
            ":".join(config.LOADING_LOG_LABELS),
            self.source_file_handler.get_target_filename(),
        )
        tx = self.graph
        cursor = tx.run(query)
        result = cursor.data()
        if len(result) == 0:
            return None
        else:
            return result[0]
