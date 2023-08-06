"""
This script provides the `Hub` class to communicate with Watchful Hub, interface
with your custom data enrichment functions and models, and perform data
enrichment on your datasets that can then be added to your Watchful projects.
"""
################################################################################


import datetime
import http.client
import json
import os
import sys
from typing import Dict, Optional

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from watchful import client, attributes
    from watchful.enricher import Enricher
except (ImportError, ModuleNotFoundError):
    import client
    import attributes
    from enricher import Enricher


class Hub:
    """
    `Hub` provides methods to interact with Watchful hub and stores the state
    about the client's access to hub. For example, once the client has logged in
    to Watchful Hub, `Hub` will store the retrieved auth token.
    """

    __host: Optional[str] = None
    __port: Optional[str] = None
    __credentials: Optional[str] = None
    __token: Optional[str] = None

    def __init__(
        self,
        credentials: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
    ) -> str:
        """
        The user must login on `Hub` initialization in order to retrieve the
        auth token needed for all other hub actions.
        """
        if host is not None and port is not None:
            self.__host = host
            self.__port = port
        elif host is None and port is None:
            self.__host = "34.127.106.236"
            self.__port = "9005"
        else:
            raise ValueError(
                "Both host and port must be strings, or both "
                "omitted to use the defaults."
            )

        self.__credentials = credentials
        if credentials is not None:
            return self.login()

    def login(
        self,
    ) -> str:
        response = self.__hub_api("login", credentials=self.__credentials)
        self.__set_token(response)
        return response

    def __hub_api(
        self,
        verb: str,
        **action: Dict[str, str],
    ) -> str:
        """
        Convenience method for Watchful Hub / collaboration API calls.
        """
        headers = {"Content-Type": "application/json"}
        if verb != "login":
            headers.update({"Authorization": f"Bearer {self.__token}"})
        action["verb"] = verb
        # Amend this for connecting from another IP to Hub IP.
        # conn = client._get_conn()
        conn = self.__get_conn()
        conn.request("POST", "/remote", json.dumps(action), headers)
        return client._read_response_summary(conn.getresponse())

    def __get_conn(
        self,
    ) -> http.client.HTTPConnection:
        return http.client.HTTPConnection(f"{self.__host}:{self.__port}")

    def __set_token(
        self,
        response: str,
    ) -> None:
        if "token" in response:
            self.__token = response["token"]
        else:
            self.__token = None
            raise ValueError("Watchful Hub did not return an auth token!")

    def __check_token_is_set(
        self,
    ) -> None:
        if not self.__token:
            return ValueError("You have yet to login to Watchful Hub!")

    def publish(
        self,
    ) -> str:
        self.__check_token_is_set(self)
        return self.__hub_api("publish")

    def fetch(
        self,
    ) -> str:
        self.__check_token_is_set(self)
        return self.__hub_api("fetch")

    def pull(
        self,
    ) -> str:
        self.__check_token_is_set(self)
        return self.__hub_api("pull")

    def push(
        self,
    ) -> str:
        self.__check_token_is_set(self)
        return self.__hub_api("push")

    def peek(
        self,
    ) -> str:
        self.__check_token_is_set(self)
        return self.__hub_api("peek")

    def enrich_dataset(
        self,
        dataset_id: str,
        custom_enricher_cls: Enricher,
        dataset_filepath: str,
        attributes_filepath: str,
    ) -> str:
        """
        Function to enrich data.
        TODO: Check if `dataset_id` is also `project_id`; if not, then the way
        to include `project_id` and or `dataset_id`.
        """
        data_enricher = custom_enricher_cls()
        # return self.__send_enriched_data_to_hub(
        #     dataset_id, data_enricher.get_enriched_data_filepath()
        # )

        test_dir_path = os.path.join(THIS_FILE_DIR, "______tests")
        attributes.enrich(
            os.path.join(test_dir_path, dataset_filepath),
            os.path.join(test_dir_path, attributes_filepath),
            data_enricher.enrich_row,
            data_enricher.enrichment_args,
        )

    def __send_enriched_data_to_hub(
        self,
        dataset_id: str,
        enriched_data_filepath: str,
    ) -> str:
        """
        Function to send enriched data to `Hub`. In `Hub`, minimally the auth
        token should be verified with the `dataset_id`. `Hub` should then push
        down the enriched data to all clients (users) of the project.
        TODO: Check if `dataset_id` is also `project_id`; if not, then the way
        to include `project_id` and or `dataset_id`.
        """
        self.__check_token_is_set(self)
        enriched_data_filename_ts = self.__append_timestamp(
            os.path.basename(enriched_data_filepath)
        )
        conn = self.__get_conn()
        
        """
        Example:
        curl -iX PUT \
          --url 'http://34.127.106.236:9005/fs/default/datasets/attrs/test_dataset_0001' \
          -H 'Content-Type: text/plain' \
          -H "Authorization: Bearer <TOKEN>" \
          -d 'test_data_0001' 
        """
        conn.request(
            "PUT",
            f"/fs/default/datasets/attrs/{dataset_id}/"
            f"{enriched_data_filename_ts}",
            open(enriched_data_filepath, "r"),
            {
                "Content-Type": "text/plain",
                "Authorization": f"Bearer {self.__token}",
            },
        )
        return client._read_response_summary(conn.getresponse())

    def __append_timestamp(
        self,
        filename: str,
    ) -> str:
        """
        Function to append timestamp to a filename, so Watchful Hub can receive
        versions of enrichment filenames in chronological order. The format of
        `timestamp` is <YYYY-MM-DD_HH-MM-SS-SSSSSS>.
        """
        timestamp = (
            str(datetime.datetime.now())
            .replace(" ", "_")
            .replace(":", "-")
            .replace(".", "-")
        )
        filename_ts = f"{os.path.splitext(filename)[0]}__{timestamp}.attrs"
        return filename_ts
