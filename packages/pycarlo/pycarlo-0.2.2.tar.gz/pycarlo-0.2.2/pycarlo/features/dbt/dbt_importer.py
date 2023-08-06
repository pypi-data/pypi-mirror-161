import json
import uuid
from typing import Optional, List, Tuple, Any, Union, Dict, Callable

import requests
from box import Box
from requests import HTTPError, ReadTimeout

from pycarlo.common import get_logger
from pycarlo.common.utils import chunks
from pycarlo.core import Client
from pycarlo.features.dbt.queries import IMPORT_DBT_MANIFEST, IMPORT_DBT_RUN_RESULTS, UPLOAD_DBT_MANIFEST

logger = get_logger(__name__)


class InvalidFileFormatException(Exception):
    pass


class DbtImporter:
    """
    Import dbt artifacts to Monte Carlo
    """

    def __init__(self,
                 mc_client: Optional[Client] = None,
                 print_func: Optional[Callable] = logger.info):
        self._mc_client = mc_client or Client()
        self._print_func = print_func

    def import_dbt_manifest(self,
                            dbt_manifest: Union[str, Dict],
                            project_name: Optional[str] = None,
                            batch_size: int = 10,
                            default_resource: Optional[str] = None) -> List[str]:
        """
        Import a dbt manifest

        :param dbt_manifest: either str indicating filename, or dict conforming to dbt manifest schema
        :param project_name: project_name to associate with manifest
        :param batch_size: import in batches of `batch_size` manifest elements
        :param default_resource: if account has multiple warehouses, define default_resource to choose
                                 the warehouse to associate with this dbt manifest. Can be either the
                                 warehouse's name or UUID

        :return: List of dbt node ID's that were successfully imported
        """
        dbt_schema_version, nodes = self._load_dbt_manifest(dbt_manifest)
        self._print_func(f"\nImporting {len(nodes)} DBT objects into Monte Carlo catalog. Please wait...")

        node_ids_imported = []
        all_bad_responses = []
        for nodes_batch in chunks(nodes, batch_size):
            node_ids, bad_responses = self._do_make_import_request(
                dbt_schema_version,
                nodes_batch,
                project_name,
                default_resource)

            if len(node_ids) > 0:
                node_ids_imported.extend(node_ids)
                self._print_func(f"Imported {len(node_ids_imported)} objects")

            all_bad_responses.extend(bad_responses)

        if all_bad_responses:
            self._print_func("\nEncountered invalid responses.", all_bad_responses)

        return node_ids_imported

    @staticmethod
    def _load_dbt_manifest(dbt_manifest: Union[str, Dict]) -> Tuple[str, List]:
        if isinstance(dbt_manifest, str):
            with open(dbt_manifest, 'r') as f:
                manifest = Box(json.load(f))
        else:
            manifest = Box(dbt_manifest)

        try:
            return manifest.metadata.dbt_schema_version, list(manifest.nodes.items())
        except KeyError:
            raise InvalidFileFormatException("Unexpected format of input file. Ensure that input file is a valid DBT manifest.json file")

    def _do_make_import_request(self,
                                dbt_schema_version: str,
                                nodes: List,
                                project_name: Optional[str],
                                default_resource: Optional[str] = None) -> Tuple[List[str], List[Any]]:
        try:
            response = self._mc_client(
                query=IMPORT_DBT_MANIFEST,
                variables=dict(
                    dbtSchemaVersion=dbt_schema_version,
                    manifestNodesJson=json.dumps(dict(nodes)),
                    projectName=project_name,
                    defaultResource=default_resource
                )
            )

            try:
                return response.import_dbt_manifest.response.node_ids_imported, []
            except KeyError:
                return [], [response]

        except (HTTPError, ReadTimeout) as e:
            if isinstance(e, ReadTimeout) or \
                    (isinstance(e, HTTPError) and e.response.status_code == requests.codes.gateway_timeout):
                self._print_func(f"Import timed out with {e}, trying again with smaller batches.")

                if len(nodes) == 1:
                    raise RuntimeError("Could not split batch any further, exiting!")

                # Possible for the request to time out if there is too much data
                # Just send each one-by-one
                all_node_ids, all_bad_requests = [], []
                for single_node_batch in chunks(nodes, 1):
                    node_ids, bad_requests = self._do_make_import_request(dbt_schema_version, single_node_batch, project_name)
                    all_node_ids.extend(node_ids)
                    all_bad_requests.extend(all_bad_requests)

                return all_node_ids, all_bad_requests
            else:
                raise

    def upload_dbt_manifest(self,
                            dbt_manifest: Union[str, Dict],
                            project_name: Optional[str] = None,
                            batch_size: int = 10,
                            default_resource: Optional[str] = None):
        """
        Upload a dbt manifest

        This is an asynchronous alternative to `import_dbt_manifest`.

        :param dbt_manifest: either str indicating filename, or dict conforming to dbt manifest schema
        :param project_name: project_name to associate with manifest
        :param batch_size: import in batches of `batch_size` manifest elements
        :param default_resource: if account has multiple warehouses, define default_resource to choose
                                 the warehouse to associate with this dbt manifest. Can be either the
                                 warehouse's name or UUID
        """
        dbt_schema_version, nodes = self._load_dbt_manifest(dbt_manifest)
        self._print_func(f'Uploading {len(nodes)} DBT objects to Monte Carlo for processing. Please wait...')

        invocation_id = str(uuid.uuid4())
        total_uploaded = 0
        for batch_index, nodes_batch in enumerate(chunks(nodes, batch_size)):
            self._do_make_upload_request(
                invocation_id,
                batch_index + 1,
                dbt_schema_version,
                nodes_batch,
                project_name,
                default_resource)

            total_uploaded += len(nodes_batch)
            self._print_func(f'Uploaded {total_uploaded} objects')

    def _do_make_upload_request(self,
                                invocation_id: str,
                                batch: int,
                                dbt_schema_version: str,
                                nodes: List,
                                project_name: Optional[str],
                                default_resource: Optional[str] = None):
        self._mc_client(
            query=UPLOAD_DBT_MANIFEST,
            variables=dict(
                invocationId=invocation_id,
                batch=batch,
                dbtSchemaVersion=dbt_schema_version,
                manifestNodesJson=json.dumps(dict(nodes)),
                projectName=project_name,
                defaultResource=default_resource
            )
        )

    def import_run_results(self,
                           dbt_run_results: Union[str, Dict],
                           project_name: Optional[str] = None,
                           run_id: Optional[str] = None,
                           run_logs: Optional[str] = None) -> int:
        """
        Import dbt run results

        :param dbt_run_results: either str indicating filename, or dict conforming to dbt run results
        :param project_name: project_name to associate with run results (Optional)
        :param run_id: run_id to associate with run results (Optional)
        :param run_logs: dbt run log output to store with run (Optional)

        :return: number of run results imported
        """
        if isinstance(dbt_run_results, str):
            with open(dbt_run_results, 'r') as f:
                dbt_run_results = Box(json.load(f))
        else:
            dbt_run_results = Box(dbt_run_results)

        try:
            dbt_schema_version = dbt_run_results.metadata.dbt_schema_version
        except KeyError:
            raise InvalidFileFormatException(
                "Unexpected format of input file. Ensure that input file is a valid DBT run_results.json file")

        response = self._mc_client(
            query=IMPORT_DBT_RUN_RESULTS,
            variables=dict(
                dbtSchemaVersion=dbt_schema_version,
                runResultsJson=json.dumps(dbt_run_results),
                projectName=project_name,
                runId=run_id,
                runLogs=run_logs
            )
        )

        try:
            num_results_imported = response.import_dbt_run_results.response.num_results_imported
        except KeyError:
            num_results_imported = 0

        self._print_func(f"\nImported a total of {num_results_imported} DBT run results into Monte Carlo\n")

        return num_results_imported