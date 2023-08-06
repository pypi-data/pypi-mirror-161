from Configs import ConfigBase
import os
import logging
import multiprocessing


class DEFAULT(ConfigBase):
    # https://docs.python.org/3/howto/logging.html#logging-levels
    LOG_LEVEL = logging.INFO
    MANAGER_LOGFILE = "./data/log/manager.log"
    WORKER_LOGFILE = "./data/log/worker.log"
    STATISTICS_LOGFILE = "./data/log/stats.log"
    DEBUG = True

    BASE_LINE_MODE = True

    PUBMED_XML_DOWNLOAD_DIR = "./data/pubmed_download/"
    # dict with params for https://py2neo.org/v4/database.html#the-graph
    # NEO4J = {"host": "192.168.178.40"}
    NEO4J = {}
    # e.g. NEO4J = {"host"="localhost",password="mypw", port=7688}

    # REDIS Cache for neobulkmp - params as dict. possible parameters see https://github.com/andymccurdy/redis-py/blob/master/redis/client.py#L750
    REDIS = {"host": "localhost"}
    STATUS_LOG_INTERVAL_SEC: int = 60
    # PUBMED_SOURCE_DIR - str
    # if set to None PMS will download all xml files from the ncbi server.
    # if set to local directory path, all xml from this path will be taken into account instead of downloading them
    #   "/tmp/"
    #   ["/tmp", "/files"]
    # if set to specific file(s) only this xml file be ingested "/tmp/pubmed20n1015.xml"
    #   "/tmp/pubmed20n1015.xml"
    #   ["/tmp/pubmed20n1015.xml","/tmp/pubmed20n1016.xml"]
    # if set to list of FTP url, only these will be downloaded and ingested
    #   "ftp://ftp.ncbi.nlm.nih.gov:21/pubmed/baseline/pubmed20n1015.xml.gz"
    #   ["ftp://ftp.ncbi.nlm.nih.gov:21/pubmed/baseline/pubmed20n1015.xml.gz", "ftp://ftp.ncbi.nlm.nih.gov:21/pubmed/baseline/pubmed20n1012.xml.gz"]
    """PUBMED_SOURCE = [
        "testdata/debug_cases.xml",
        "testdata/single.xml",
    ]"""
    """
    PUBMED_SOURCE = [
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1009.xml.gz",
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1010.xml.gz",
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1012.xml.gz",
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1013.xml.gz",
    ]
    """
    """
    PUBMED_SOURCE = [
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1009.xml.gz",
        "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed20n1010.xml.gz",
    ]
    """
    # PUBMED_SOURCE = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/pubmed21n0670.xml.gz"

    # Download latest 5 files
    # PUBMED_SOURCE = 5

    # Download All
    PUBMED_SOURCE = None

    # Tiny test
    # PUBMED_SOURCE = "testdata/single.xml"

    REDOWNLOAD_EXTISTING_PUBMED_XMLS = False
    MAX_WORKER_COUNT = multiprocessing.cpu_count()
    MIN_PARSING_WORKERS_COUNT = 3
    MAX_RETRIES_ON_DOWNLOAD_ERRORS = 6
    MAX_RETRIES_ON_INSERT_ERRORS = 4

    # ARTICLE_FLUSH_INTERVAL
    # load articles to cache every n articles. A higher value spares the cache in terms of connections/requests per second but uses more memory on the parser side
    ARTICLE_FLUSH_INTERVAL = 500
    # commit every n nodes per graphio nodeset
    GRAPHIO_BATCHSIZE = 100000
    # The Document type definition (dtd) file is used in Pubmedsucker to determine wether an elemnt in the source xml is a list or an single attribute.
    # it can be a local file or a url
    # it will be cached locally if it is an url and is used for multiple worker
    XML_DTD_SOURCE = "http://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd"

    # PUBMED_FTP_SERVER_CONFIG - dict
    # see config schema from https://git.connect.dzd-ev.de/dzdtools/pythonmodules/tree/master/FTPDownloader

    @property
    def PUBMED_FTP_SERVER_CONFIG(self):
        # quick and dirty solution for https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/issues/14
        return {
            "url": "ftp.ncbi.nlm.nih.gov",
            "port": 21,
            "user": "anonymous",
            "pw": "anonymous",
            "base_path": None,
            "dest_path": self.PUBMED_XML_DOWNLOAD_DIR,
            "not_to_save_extentions": ["md5", "txt", "html"],
            "overwrite_existing": False,
            "verify_file": True,
            "verify_throw_error_when_failed": True,
            "verify_fallback_to_size_comparison": False,
        }

    # path for base line xmls ( https://www.nlm.nih.gov/databases/download/pubmed_medline.html ) on the NIH ftp server
    PUBMED_BASE_LINE_PATH = "/pubmed/baseline/"
    # path for udpated xmls ( https://www.nlm.nih.gov/databases/download/pubmed_medline.html ) on the NIH ftp server
    PUBMED_UPDATE_PATH = "/pubmed/updatefiles/"

    EXIT_WHEN_DONE = True

    LOADING_LOG_LABELS = ["_PubMedXmlLoadingLog"]

    FORCE_REMERGING_LOADED_PUBMED_XMLS = False

    # This is a limit to prevent the cache on overusing memory. If you have enough free memory you can increase this value
    # if you are short on memory or even had crashed due to low memory it can help to decrease this value.
    # this can impact perfomance
    MAX_NODES_N_RELS_IN_CACHE_BEFORE_PAUSING_PARSING = 10000000

    # Filter rules applied on each article. if positive whole article with all metadata will not be saved
    # FILTER_RULES = 'Author.ForeName == "Connie" and (Keyword.Keyword == "Spinal diseases" or MeshQualifier.text == "physiology")'
    FILTER_RULES = None


class DEV(DEFAULT):
    PUBMED_SOURCE="testdata/debug_cases.xml"
