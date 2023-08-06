from unittest import TestCase
from unittest.mock import Mock

from pycarlo.features.dbt import DbtCloudClient
from pycarlo.features.dbt import DbtCloudImporter
from pycarlo.features.dbt import DbtImporter
from pycarlo.features.dbt.queries import CREATE_PROJECT


class DbtCloudImporterTest(TestCase):
    def test_import_dbt_cloud(self):
        dbt_cloud_client = Mock(spec=DbtCloudClient)
        dbt_importer = Mock(spec=DbtImporter)
        client_mock = Mock()

        dbt_cloud_importer = DbtCloudImporter(
            dbt_cloud_client=dbt_cloud_client,
            dbt_importer=dbt_importer,
            client=client_mock
        )

        dbt_cloud_client.get_projects.return_value = ({}, [
            {
                'id': 100,
                'name': 'my dbt project'
            }
        ])

        dbt_cloud_client.get_jobs.return_value = ({}, [
            {
                'id': 200,
                'name': 'my job'
            }
        ])

        dbt_cloud_client.get_runs.return_value = ({}, [
            {
                'id': 300,
                'is_complete': True,
                'project_id': 100,
                'run_steps': [
                    {
                        'logs': 'log 1'
                    },
                    {
                        'logs': 'log 2'
                    },
                ]
            }
        ])

        def mock_get_artifact(run_id: str, artifact_path: str):
            return {'mock_artifact': artifact_path}
        dbt_cloud_client.get_run_artifact.side_effect = mock_get_artifact

        dbt_cloud_importer.import_dbt_cloud()

        # Should have created a project
        client_mock.assert_called_once_with(
            query=CREATE_PROJECT,
            variables=dict(
                projectName=100,
                source='DBT_CLOUD'
            )
        )

        dbt_importer.import_dbt_manifest.assert_called_once_with(
            dbt_manifest={
                'mock_artifact': 'manifest.json'
            },
            project_name=100,
            default_resource=None
        )

        dbt_importer.import_run_results.assert_called_once_with(
            dbt_run_results={
                'mock_artifact': 'run_results.json'
            },
            project_name=100,
            run_id=300,
            run_logs='log 1\nlog 2'
        )

        # Test with setting default_resource
        dbt_importer.reset_mock()
        dbt_cloud_importer.import_dbt_cloud(default_resource='snowflake')
        dbt_importer.import_dbt_manifest.assert_called_once_with(
            dbt_manifest={
                'mock_artifact': 'manifest.json'
            },
            project_name=100,
            default_resource='snowflake'
        )
