import logging
from pms.tools import get_graph
from Configs import getConfig
from DZDutils.neo4j import run_periodic_iterate

config = getConfig()

log = logging.getLogger("PubmedSuckerFinalTransform")


def delete_old_articles() -> int:
    count_before = get_graph().run("MATCH (n:_PubMedArticle_delete_notification) return count(n) as cnt").data()[0]["cnt"]
    run_periodic_iterate(
        graph=get_graph(),
        cypherIterate="MATCH (n:_PubMedArticle_delete_notification) return n as ART_DEL",
        cypherAction="""MATCH (a:PubMedArticle{PMID:ART_DEL.PMID})
                    OPTIONAL MATCH (a)-[*1..2]->(n)
                    WHERE n:ELocationID OR n:Abstract OR n:AbstractText OR n:ArticleId OR n:ReferenceList OR n:Reference OR n:GrantList OR n:GeneralNote OR n:Contribution OR n:KeywordList OR n:MeshHeadingList OR n:MeshHeading OR n:PersonalNameSubjectList
                    DETACH DELETE a,n, ART_DEL
                    return count(distinct a) as cnt""",
        batchSize=100,
        parallel=False,
    )
    count_after = get_graph().run("MATCH (n:_PubMedArticle_delete_notification) return count(n) as cnt").data()[0]["cnt"]
    deleted_count = count_before - count_after
    get_graph().run("MATCH (n:_PubMedArticle_delete_notification) DETACH DELETE n")
    return deleted_count


def run_transforming_queries():
    log.info("Detach MedLineJournal info from article and connect it to Journal")
    run_periodic_iterate(
        graph=get_graph(),
        cypherIterate="MATCH (p:PubMedArticle)-[r:PUBMEDARTICLE_HAS_JOURNALISSUE]->(ji:JournalIssue)-[jij:JOURNALISSUE_HAS_JOURNAL]->(j:Journal) return p as article,j as journal",
        cypherAction="MATCH (article)-[rj:PUBMEDARTICLE_HAS_MEDLINEJOURNALINFO]->(mji:MedlineJournalInfo) MERGE (journal)-[:JOURNAL_HAS_MEDLINEJOURNALINFO]->(mji) DELETE rj",
        batchSize=100,
        parallel=False,
    )
