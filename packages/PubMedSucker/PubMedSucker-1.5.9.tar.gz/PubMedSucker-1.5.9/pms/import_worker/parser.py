import xmltodict
import json
import os
from dict2graph import Dict2graph
from Configs import getConfig
import logging
from uuid import uuid4
from py2neo import Graph
from DZDutils.neo4j import run_periodic_iterate

# from py2neo.client import TransactionError, BrokenTransactionError
from pms.tools import DTDUtil, get_graph
from pms.import_worker.filter import Filter
from pms.import_worker.pubmed_source_file_handler import PubMedSourceFileHandler

from typing import Dict, List
from neobulkmp.cache_backend import CacheInterface
from neobulkmp import WorkerSourcing

config = getConfig()


class PubMedXMLParser:
    # Parent Worker process
    worker: WorkerSourcing = None

    def __init__(
        self,
        parent_worker: WorkerSourcing,
        xml_file_handler: PubMedSourceFileHandler,
        debug: bool = False,
    ):
        self.articles_parsed_count = 0
        self.articles_failed_parsing_count = 0
        self.articles_in_memory_count = 0
        self.articles_loaded_to_db_count = 0
        self.xml_file_handler = xml_file_handler
        self.dtd = DTDUtil(config.XML_DTD_SOURCE)
        self.delete_pmids: List = []
        self.d2g = Dict2graph()
        self.d2g._debug = debug
        self._set_config()
        self.filter = Filter(config.FILTER_RULES)
        self.worker = parent_worker
        self.graph_connection_params = config.NEO4J
        self.xml_file = self.worker.source_file_handler.get_target_filename()

    def run(self, cache: CacheInterface):
        self.cache = cache
        self.graph = Graph(**self.graph_connection_params)

        with self.worker.source_file_handler.open_file() as f:
            xmltodict.parse(
                f,
                item_depth=2,
                item_callback=self._handle_article_callback,
                disable_entities=False,
                force_list=self._force_list,
                postprocessor=self._xmltodict_postprocessor,
                attr_prefix="",
                cdata_key="text",
                dict_constructor=dict,
                strip_whitespace=True,
                cdata_separator="###CD###"
                # force_cdata=True,
            )
        # Flush last articles
        self._load_to_db()

    def _node_adding_callback(self, node):
        if node.__primarylabel__ == "PubMedArticle":
            node["xml_source_file"] = os.path.basename(self.xml_file)
        if node.__primarylabel__ == "Keyword":
            if "text" in node and node["text"] is not None:
                node["text_lower"] = node["text"].lower().strip()
        return node

    def _parse_DeleteCitation(self,article) -> List[int]:
        # parse https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/190101/el-DeleteCitation.html
        # this element comes is a varity of undefined formats :/ . lets try to catch them all
        pmids = []
        if isinstance(article["PMID"],dict):
            pmids.append(article["PMID"]["text"])
        elif isinstance(article["PMID"],list):
            for pmid in article["PMID"]:
                if isinstance(pmid,dict):
                    pmids.append(pmid["text"])
                elif isinstance(pmid,int) or isinstance(pmid,str):
                    pmids.append(pmid)
                else:
                    self.worker.log.exception(f"Can not parse 'DeleteCitation'. Unexpected format: '{json.dumps(article)}'")
        elif isinstance(article["PMID"],int) or isinstance(article["PMID"],str):
            pmids.append(article["PMID"])
        else:
            self.worker.log.exception(f"Can not parse 'DeleteCitation'. Unexpected format: '{json.dumps(article)}'")
        return pmids

    def _handle_article_callback(self, path, article):
        try:
            if path == [("PubmedArticleSet", None), ("DeleteCitation", None)]:
                self.delete_pmids.extend(self._parse_DeleteCitation(article))
            elif path == [("PubmedArticleSet", None), ("PubmedArticle", None)]:
                self.d2g.parse(article, "PubMedArticle", instant_save=False)
                # if self.filter.pass_filter(self.d2g):
                #    self.d2g.save()
                self.d2g.save()
                self.articles_parsed_count += 1
                self.articles_in_memory_count += 1
        except Exception as e:
            message = f"Parsing failure for article in xml {self.xml_file}. Article json: \n-------------\n {json.dumps(article)} \n-------------\n"
            self.worker.log.exception(message)
            # log.exception(message)

            self.articles_failed_parsing_count += 1

        if self.articles_in_memory_count >= config.ARTICLE_FLUSH_INTERVAL:
            self._load_to_db()

        return True

    def _load_to_db(self):
        for nodeSet in self.d2g.nodeSets.values():
            self.worker.store_graphSet(nodeSet)
            # self.worker.cache.store_NodeSet(nodeSet)

        for relSet in self.d2g.relationshipSets.values():
            self.worker.store_graphSet(relSet)
            # self.worker.cache.store_RelSet(relSet)

        self.articles_loaded_to_db_count += self.articles_in_memory_count
        self.articles_in_memory_count = 0
        self.d2g.clear()
        self._mark_to_be_deleted_articles()

    def _mark_to_be_deleted_articles(self):
        run_periodic_iterate(
            graph=get_graph(),
            cypherIterate="UNWIND $pmids as pm_id return pm_id",
            cypherAction="CREATE (n:_PubMedArticle_delete_notification{PMID:pm_id})",
            parallel=False,
            params={"pmids": self.delete_pmids},
            _log_status_func=self.worker.log.debug,
        )
        self.delete_pmids = []

    def _xmltodict_postprocessor(self, path, key, value):
        # some texts come with html tags in it (<b>,<i>,<sup>...). see https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/190101/el-b.html
        # xmltodict can not distinguish between xml and html tags.
        # this is a quick, messy, dirty hack. it can destory the correct sequence of html tags texts and hits the perfomance; see https://github.com/martinblech/xmltodict/issues/63 and https://github.com/martinblech/xmltodict/issues/247
        # todo: fix 247 issue
        if key in [
            "ArticleTitle",
            "Affiliation",
            "CollectionTitle",
            "AbstractText",
            "Keyword",
            "CollectiveName",
            "VolumeTitle",
            "Citation",
            "PublisherName",
            "Title",
        ]:
            """
            hack to fix html tags in text
            {[('b', ['Symptomatic']), ('text', 'Unusual  Multipartite Patella Associated with Quadriceps Fat Pad Edema.')]}
            """
            try:
                if isinstance(value, dict):
                    tag_texts = []
                    pubmed_html_tag = [
                        "b",
                        "i",
                        "sup",
                        "sub",
                        "u",
                        "mml:math",
                        "DispFormula",
                    ]
                    if "text" in value:
                        result_val = value["text"]
                    else:
                        result_val = None
                    if result_val is not None:
                        for propname, item in value.items():
                            if propname in pubmed_html_tag:
                                if not isinstance(item, list):
                                    vals = [item]
                                else:
                                    vals = item
                                for val in vals:
                                    if isinstance(val, dict):
                                        val = json.dumps(val)
                                    if val:
                                        result_val = result_val.replace(
                                            "###CD###", val, 1
                                        )

                    else:
                        for propname, item in value.items():
                            if propname in pubmed_html_tag:

                                if not isinstance(item, list):
                                    vals = [item]
                                else:
                                    vals = item
                                result_val += " " + " ".join(item)
                    return (key, result_val)
            except Exception as e:
                self.worker.log.warning(
                    "----------\nError postprocessing {KEY} with value '{VAL}'. \n WARNING: The information will be lost and not saved ".format(
                        KEY=key, VAL=value
                    )
                )
                return (key, "PARSER_ERROR_NO_VALUE")

        elif isinstance(value, dict) and "text" in value:
            value["text"] = (
                value["text"].replace("###CD###\n", "").replace("###CD###", "").strip()
            )
            if not value["text"]:
                del value["text"]
        elif isinstance(value, str):
            value = value.replace("###CD###\n", "").replace("###CD###", "").strip()
        return (key, value)

    def _force_list(self, path, key, value):
        """example:
        path:   [('PubmedArticleSet', None), ('PubmedArticle', None), ('MedlineCitation', OrderedDict([('Status', 'Publisher'), ('Owner', 'NLM')])), ('Article', OrderedDict([('PubModel', 'Print-Electronic')])), ('AuthorList', OrderedDict([('CompleteYN', 'Y')]))]
        key:    Author
        value:  OrderedDict([('@ValidYN', 'Y'), ('LastName', 'Kalla'), ('ForeName', 'Roger'), ('Initials', 'R'), ('AffiliationInfo', OrderedDict([('Affiliation', 'Department of Neurology, University Hospital Bern, Bern. Switzerland.')]))])
        """
        if key in ["Chemical"]:
            return False
        return self.dtd.is_list_element(path, key)

    def _set_config(self):

        # find all dict2graph (d2g) config variables here https://git.connect.dzd-ev.de/dzdpythonmodules/dict2graph#content

        # lock allowed labels to prevent unknown/new xml objects
        self.d2g.config_list_allowlist_nodes = [
            "Abstract",
            "AbstractText",
            # "AccessionNumber",
            "Affiliation",
            "ArticleId",
            "Author",
            "Identifier",
            "Chemical",
            "ChemicalList",
            "Contribution",
            "DataBank",
            "Date",
            "Gene",
            "GeneSymbolList",
            "GeneralNote",
            "Grant",
            "GrantList",
            "ISSN",
            "Investigator",
            "Journal",
            "JournalIssue",
            "Keyword",
            "KeywordList",
            "Language",
            "MedlineJournalInfo",
            "MeshDescriptor",
            "MeshHeading",
            "MeshHeadingList",
            "MeshQualifier",
            "PersonalNameSubject",
            "PersonalNameSubjectList",
            "PubMedArticle",
            "PublicationType",
            "Reference",
            "ReferenceList",
        ]

        self.d2g.config_dict_blocklist_props = {
            "Author": ["ValidYN"],
            "ArticleId": ["ValidYN"],
            "Date": ["DateType"],
            #  "The @DateType will always be present and will always indicate "Electronic"." we can ignore this -> https://dtd.nlm.nih.gov/ncbi/pubmed/doc/out/190101/el-ArticleDate.html
        }

        self.d2g.config_list_allowlist_collection_hubs = ["None"]
        self.d2g.config_dict_label_override = {
            "ArticleDate": {"Date": {"type": "ArticleDate"}},
            "PubDate": {"Date": {"type": "PubDate"}},
            "PubMedPubDate": {"Date": {"type": "PubMedPubDate"}},
            "DateCompleted": {"Date": {"type": "DateCompleted"}},
            "DateRevised": {"Date": {"type": "DateRevised"}},
            "AffiliationInfo": "Affiliation",
            "DescriptorName": "MeshDescriptor",
            "QualifierName": "MeshQualifier",
            "OtherAbstract": {"Abstract": {"OtherAbstract": True}},
            "OtherID": {"ArticleId": {"OtherId": True}},
            "ELocationID": {"ArticleId": {"ELocationID": True}},
            "AuthorListAuthor": "Author",
            "GeneSymbol": "Gene",
        }

        self.d2g.config_dict_property_name_override = {
            "PubMedArticle": {
                "PMIDtext": "PMID",
                # "PublicationTypetext": "PublicationType",
            },
            "ArticleId": {"text": "ID", "Source": "IdType"},
            "Chemical": {"NameOfSubstance-UI": "UI", "text": "Name"},
            "DataBank": {"DataBankName": "Name"},
            "Gene": {"GeneSymbol": "sid"},
            "ISSN": {"text": "ID"},
            "AccessionNumber": {"AccessionNumber": "ID"},
            "Identifier": {"text": "ID"},
            "AbstractText": {"AbstractText": "text"},
        }
        self.d2g.config_list_deconstruction_limit_nodes = []
        self.d2g.config_dict_primarykey_attr_by_label = {
            "PubMedArticle": "PMID",
            "Identifier": "ID",
            "Keyword": "text",
            "ArticleId": "ID",
            "PublicationType": "UI",
            "MeshDescriptor": "UI",
            "MeshQualifier": "UI",
            "Chemical": "UI",
            # "AccessionNumber": "ID",
            "Gene": "Name",
            "ISSN": "ID",
            "MedlineJournalInfo": "MedlineTA",
            "DataBank": "name",
        }
        self.d2g.config_dict_primarykey_generated_hashed_attrs_by_label = {
            "Date": "AllAttributes",
            "JournalIssue": "AllContent",
            "Journal": "AllAttributes",
            "MeshHeadingList": "AllContent",
            "MeshHeading": "AllContent",
            "AbstractText": ["text"],
            "Abstract": "InnerContent",
            "ArticleIdList": "InnerContent",
            "Author": "OuterContent",
            "KeywordList": "OuterContent",
            "ReferenceList": "AllContent",
            "Grant": "AllAttributes",
            "Investigator": "AllAttributes",
            "PersonalNameSubject": "AllAttributes",
            "PersonalNameSubjectList": "AllContent",
            "ChemicalList": "AllContent",
            "GrantList": "AllContent",
            "GeneralNote": ["text"],
            "Reference": ["Citation"],
            "Affiliation": "AllAttributes",
            "GeneSymbolList": "InnerContent",
        }
        self.d2g.config_dict_flip_nodes = {"Journal": "JournalIssue"}

        self.d2g.config_list_throw_away_nodes_with_empty_key_attr = [
            "Keyword",
            "ArticleId",
            "DataBank",
            # "AccessionNumber",
            "Chemical",
            "MedlineJournalInfo",
        ]
        self.d2g.config_list_throw_away_from_nodes = [
            "History",
            "Pagination",
            "SupplMeshList",
            "CommentsCorrectionsList",
        ]

        self.d2g.config_dict_node_prop_to_rel_prop = {
            "Keyword": {"MajorTopicYN": ["KEYWORDLIST_HAS_KEYWORD"]},
            "MeshDescriptor": {"MajorTopicYN": ["MESHHEADING_HAS_MESHDESCRIPTOR"]},
            "MeshQualifier": {"MajorTopicYN": ["MESHHEADING_HAS_MESHDESCRIPTOR"]},
            "Date": {"type": ["JOURNALISSUE_HAS_DATE", "PUBMEDARTICLE_HAS_DATE"]},
            "Author": {"EqualContrib": ["CONTRIBUTION_HAS_AUTHOR"]},
        }

        # self.d2g.config_dict_concat_list_attr = {"PubMedArticle": {"Language": ", "}}

        # selectively flatten the json
        self.d2g.config_dict_interfold_json_attr = {
            "PubMedArticle": {
                "MedlineCitation": {"combine_attr_names": False},
                "PubmedData": {"combine_attr_names": False},
                "Article": {"combine_attr_names": False},
                "AuthorList": {"combine_attr_names": True},
                "InvestigatorList": {"combine_attr_names": False},
                "ArticleIdList": {"combine_attr_names": False},
                "DataBankList": {"combine_attr_names": False},
                "PMID": {"combine_attr_names": True},
                "PublicationTypeList": {"combine_attr_names": False},
                "PersonalNameSubjectList": {"combine_attr_names": False},
                # "PublicationType": {"combine_attr_names": True},
            },
            "Reference": {"ArticleIdList": {"combine_attr_names": False}},
            # "DataBank": {"AccessionNumberList": {"combine_attr_names": False}},
            "Chemical": {"NameOfSubstance": {"combine_attr_names": False}},
        }

        self.d2g.config_dict_hubbing = {
            "PubMedArticle": [
                {
                    "hub_member_labels": ["Author", "Affiliation"],
                    "hub_label": "Contribution",
                    "hub_id_from": "edge",
                },
                {
                    "hub_member_labels": ["Investigator", "Affiliation"],
                    "hub_label": "Contribution",
                    "hub_id_from": "edge",
                },
            ]
        }

        self.d2g.config_func_node_post_modifier = self._node_adding_callback

        self.d2g.make_distinct_before_insert = False
