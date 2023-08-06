import os


from Configs import getConfig
from py2neo import Graph
from FTPDownloader import FTPDownloader

## DTDUtils imports
import io
from lxml import etree
from memoization import cached
from time import sleep

config = getConfig()


def create_config_dirs():
    pathes = [
        config.MANAGER_LOGFILE,
        config.WORKER_LOGFILE,
        config.STATISTICS_LOGFILE,
    ]
    for path in pathes:
        if "." in os.path.basename(path):
            # TODO: hats a dirty,dirty hack! but works for now
            path = os.path.dirname(path)
        os.makedirs(path, exist_ok=True)


def get_graph():
    return Graph(**config.NEO4J)


def get_phase1_file_list():
    file_list = []
    ftp_conf = config.PUBMED_FTP_SERVER_CONFIG
    if config.BASE_LINE_MODE:
        ftp_conf["base_path"] = config.PUBMED_BASE_LINE_PATH
    else:
        ftp_conf["base_path"] = config.PUBMED_UPDATE_PATH
    if isinstance(config.PUBMED_SOURCE, list):
        # list of local or remore files
        for source in config.PUBMED_SOURCE:
            file_list.append({"xml_url": source})
    elif isinstance(config.PUBMED_SOURCE, str):
        if os.path.isdir(config.PUBMED_SOURCE):
            # directory of local files
            for file in [
                f
                for f in os.listdir(config.PUBMED_SOURCE)
                if os.path.isfile(os.path.join(config.PUBMED_SOURCE, f))
                and f.endswith("xml")
            ]:
                file_list.append({"xml_url": os.path.join(config.PUBMED_SOURCE, file)})
        else:
            # single remote or lcoal file
            file_list.append({"xml_url": config.PUBMED_SOURCE})
    elif isinstance(config.PUBMED_SOURCE, int) or config.PUBMED_SOURCE is None:
        # first n files of remote dir
        downloader = FTPDownloader.from_config_dict(ftp_conf)
        remote_file_list = downloader.get_remote_file_list(include_full_url=True)
        if config.PUBMED_SOURCE is None:
            file_list = [{"xml_url": url} for url in remote_file_list]
        else:
            file_list = [
                {"xml_url": url}
                for url in remote_file_list[config.PUBMED_SOURCE * -1 :]
            ]
    return file_list


class DTDUtil(object):
    cache_path = ".cache/dtd_util"
    no_cache = False

    def __init__(self, dtd_file):
        try:
            self._source_file = self.download_dtd(dtd_file)
        except ValueError:  # invalid URL. use path as local file
            self._source_file = dtd_file
        self._parse_dtd()

    def download_dtd(self, url: str):
        import urllib.request

        # TODO: urllib.request.urlopen can be very slow if ipv6 is enabled. investigate workaround
        url_parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(url_parsed.path)
        cache_dir = os.path.join(self.cache_path, url_parsed.netloc)
        cache_path = os.path.join(cache_dir, filename)
        if os.path.isfile(cache_path):
            # file is allready downloaded
            # bad hack. wait some ms if file is still in downloading request by another process

            # tb: 2020_11_26...this still make problems on high scaling (many workers). hotfixed the hack by preloading dtd in the main.py
            sleep(1)
            return cache_path
        os.makedirs(cache_dir, exist_ok=True)
        with urllib.request.urlopen(url) as response:
            with open(cache_path, "w") as target_file:
                target_file.write(response.read().decode("utf-8"))
        # content = response.read().decode("utf-8")
        return cache_path

    def _parse_dtd(self):
        if isinstance(self._source_file, str):
            try:
                self.dtd = etree.DTD(self._source_file)
            except:
                raise
        else:
            # TODO: I dont why i need to reconvert to a string->StringIO ("io.StringIO(file.getvalue())") object here when running in a sub processes? It does not work when directly using the "file"-io.stringIO object (Which is not empty or so).
            # Investigate!
            self.dtd = etree.DTD(io.StringIO(self._source_file.getvalue()))

    @cached
    def is_list_element(self, path, key):

        """example vals
        PATH [('PubmedArticleSet', None), ('PubmedArticle', None), ('MedlineCitation', OrderedDict([('Status', 'Publisher'), ('Owner', 'NLM')])), ('Article', OrderedDict([('PubModel', 'Print-Electronic')])), ('AuthorList', OrderedDict([('CompleteYN', 'Y')]))]
        KEY Author
        """
        if len(path) <= 1:
            # we are at the root element. it can not be a list element
            return False

        parent_key = path[len(path) - 1][0]
        dtd_el = next(
            (x for x in self.dtd.iterelements() if x.name == key),
            None,
        )
        if dtd_el is None:
            return False
        parent_dtd_el = next(
            (x for x in self.dtd.iterelements() if x.name == parent_key),
            None,
        )
        # get a binary tree of contents types of parent
        # BTW: Fuck binary trees in python
        # http://lxml.de/validation.html#id1

        """
        <!ELEMENT	Article (Journal,ArticleTitle,((Pagination, ELocationID*) | ELocationID+),
                     Abstract?,AuthorList?, Language+, DataBankList?, GrantList?,
                     PublicationTypeList, VernacularTitle?, ArticleDate*) >
        """
        """<!ELEMENT	BookDocument ( PMID, ArticleIdList, Book, LocationLabel*, ArticleTitle?, VernacularTitle?,
                        Pagination?, Language*, AuthorList*, InvestigatorList?, PublicationType*, Abstract?, Sections?, KeywordList*, 
                        ContributionDate?, DateRevised?, GrantList?, ItemList*, ReferenceList*) >
        """
        """<!ELEMENT	PubmedArticleSet ((PubmedArticle | PubmedBookArticle)+, DeleteCitation?) >
            <!ATTLIST       PubmedArticleSet
            >

            <!ELEMENT	PubmedArticleSet ((PubmedArticle | PubmedBookArticle)+, DeleteCitation?) >
            <!ATTLIST       PubmedArticleSet
            >
        """

        dtd_el, is_multi = next(
            (
                x
                for x in self.traverse_content_elements(parent_dtd_el.content, False)
                if x[0].name == key
            ),
            (dtd_el, None),
        )
        return is_multi or False

    def traverse_content_elements(self, tree, is_multi):

        if tree.occur in ["mult", "plus"]:
            is_multi = True
        if tree.left is not None:
            yield from self.traverse_content_elements(tree.left, is_multi)

        yield tree, is_multi

        if tree.right is not None:
            yield from self.traverse_content_elements(tree.right, is_multi)
