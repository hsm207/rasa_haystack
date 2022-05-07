import logging
import tempfile
from typing import Any, Dict, List, Text
import urllib.request

import requests
import wikipedia
from haystack.document_stores import ElasticsearchDocumentStore
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from haystack.utils import convert_files_to_dicts, clean_wiki_text

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
logger = logging.getLogger(__name__)


def get_wikipedia_articles(data_dir, topics=[]):
    for topic in topics:
        article = wikipedia.page(topic).content
        with open(f"{data_dir}/{topic}.txt", "w") as f:
            f.write(article)

def get_pdf_files(data_dir):
    fileurls = ["https://arxiv.org/pdf/2107.07567.pdf", "https://arxiv.org/pdf/2108.11463.pdf"]
    filenames = ["blenderbot.pdf", "bookings.pdf"]

    for fileurl, filename in zip(fileurls, filenames):
        urllib.request.urlretrieve(fileurl, f"{data_dir}/{filename}")

def convert_articles_to_docs(data_dir):
    return convert_files_to_dicts(
        dir_path=data_dir, clean_func=clean_wiki_text, split_paragraphs=True
    )


class ActionAnswerQuestion(Action):
    doc_store = ElasticsearchDocumentStore(
        host="elasticsearch", username="", password="", index="document"
    )
    haystack_endpoint = "http://haystack-api:8000/query"
    topics = ["Osteopathy", "Osteopathic medicine in the United States"]

    def __init__(self) -> None:
        logger.debug(f"Creating {self.name()} custom action ...")

        with tempfile.TemporaryDirectory() as data_dir:

            logger.info(f"Saving wikipedia articles to {data_dir}")
            get_wikipedia_articles(data_dir, topics=self.topics)

            logger.info(f"Downloading pdf articles to {data_dir}")
            get_pdf_files(data_dir)

            logger.info(f"Converting files in {data_dir} to haystack documents ...")
            docs = convert_articles_to_docs(data_dir)

            logger.info("Writing haystack documents to document store")
            self.doc_store.write_documents(docs)

    def _build_headers(self):
        return {"Content-Type": "application/json"}

    def _build_payload(self, question):
        return {"query": question}

    def _get_answer(self, question):
        headers = self._build_headers()
        payload = self._build_payload(question)

        return requests.request(
            "POST", self.haystack_endpoint, headers=headers, json=payload
        ).json()

    def name(self) -> Text:
        return "action_answer_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        question = tracker.latest_message["text"]

        r = self._get_answer(question)

        candidate_answers = r["answers"]
        logging.info(f"Candidate answers are: {candidate_answers}")

        if candidate_answers and candidate_answers[0]["score"] > 0.70:
            answer = candidate_answers[0]["answer"]
        else:
            answer = "I don't know the answer"

        dispatcher.utter_message(text=answer)

        return []
