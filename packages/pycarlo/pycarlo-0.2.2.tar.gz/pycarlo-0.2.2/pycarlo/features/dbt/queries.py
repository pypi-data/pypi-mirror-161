IMPORT_DBT_MANIFEST = """
mutation importDbtManifest($dbtSchemaVersion: String!, $manifestNodesJson: String!, $projectName: String, $defaultResource: String) {
  importDbtManifest(
    dbtSchemaVersion: $dbtSchemaVersion,
    manifestNodesJson: $manifestNodesJson,
    projectName: $projectName,
    defaultResource: $defaultResource
  ) {
    response {
      nodeIdsImported
    }
  }
}
"""

UPLOAD_DBT_MANIFEST = """
mutation uploadDbtManifest($invocationId: String!, $batch: Int, $dbtSchemaVersion: String!, $manifestNodesJson: String!, $projectName: String, $defaultResource: String) {
  uploadDbtManifest(
    invocationId: $invocationId,
    batch: $batch,
    dbtSchemaVersion: $dbtSchemaVersion,
    manifestNodesJson: $manifestNodesJson,
    projectName: $projectName,
    defaultResource: $defaultResource
  ) {
    ok
  }
}
"""

IMPORT_DBT_RUN_RESULTS = """
mutation importDbtRunResults($dbtSchemaVersion: String!, $runResultsJson: String!, $projectName: String, $runId: String, $runLogs: String) {
  importDbtRunResults(
    dbtSchemaVersion: $dbtSchemaVersion,
    runResultsJson: $runResultsJson,
    projectName: $projectName,
    runId: $runId,
    runLogs: $runLogs
  ) {
    response {
      numResultsImported
    }
  }
}
"""

CREATE_PROJECT = """
mutation createDbtProject($projectName: String!, $source: DbtProjectSource!) {
  createDbtProject(
    projectName: $projectName,
    source: $source
  ) {
    dbtProject {
      projectName
      source
    }
  }
}
"""