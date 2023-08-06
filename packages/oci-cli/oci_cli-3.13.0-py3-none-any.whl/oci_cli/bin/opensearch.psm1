function GetOciTopLevelCommand_opensearch() {
    return 'opensearch'
}

function GetOciSubcommands_opensearch() {
    $ociSubcommands = @{
        'opensearch' = 'opensearch-cluster opensearch-cluster-backup'
        'opensearch opensearch-cluster' = 'opensearch-cluster opensearch-cluster-collection opensearch-versions-collection work-request work-request-collection work-request-error-collection work-request-log-entry-collection'
        'opensearch opensearch-cluster opensearch-cluster' = 'backup create delete get opensearch-cluster-restore resize-opensearch-cluster-horizontal resize-opensearch-cluster-vertical update'
        'opensearch opensearch-cluster opensearch-cluster-collection' = 'list-opensearch-clusters'
        'opensearch opensearch-cluster opensearch-versions-collection' = 'list-opensearch-versions'
        'opensearch opensearch-cluster work-request' = 'get'
        'opensearch opensearch-cluster work-request-collection' = 'list-work-requests'
        'opensearch opensearch-cluster work-request-error-collection' = 'list-work-request-errors'
        'opensearch opensearch-cluster work-request-log-entry-collection' = 'list-work-request-logs'
        'opensearch opensearch-cluster-backup' = 'opensearch-cluster-backup opensearch-cluster-backup-collection'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup' = 'delete get update'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup-collection' = 'list-opensearch-cluster-backups'
    }
    return $ociSubcommands
}

function GetOciCommandsToLongParams_opensearch() {
    $ociCommandsToLongParams = @{
        'opensearch opensearch-cluster opensearch-cluster backup' = 'compartment-id display-name from-json help if-match max-wait-seconds opensearch-cluster-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster create' = 'compartment-id data-node-count data-node-host-bare-metal-shape data-node-host-memory-gb data-node-host-ocpu-count data-node-host-type data-node-storage-gb defined-tags display-name freeform-tags from-json help master-node-count master-node-host-bare-metal-shape master-node-host-memory-gb master-node-host-ocpu-count master-node-host-type max-wait-seconds opendashboard-node-count opendashboard-node-host-memory-gb opendashboard-node-host-ocpu-count software-version subnet-compartment-id subnet-id system-tags vcn-compartment-id vcn-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster delete' = 'force from-json help if-match max-wait-seconds opensearch-cluster-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster get' = 'from-json help opensearch-cluster-id'
        'opensearch opensearch-cluster opensearch-cluster opensearch-cluster-restore' = 'compartment-id from-json help if-match max-wait-seconds opensearch-cluster-backup-id opensearch-cluster-id prefix wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster resize-opensearch-cluster-horizontal' = 'data-node-count defined-tags freeform-tags from-json help if-match master-node-count max-wait-seconds opendashboard-node-count opensearch-cluster-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster resize-opensearch-cluster-vertical' = 'data-node-host-memory-gb data-node-host-ocpu-count data-node-storage-gb defined-tags freeform-tags from-json help if-match master-node-host-memory-gb master-node-host-ocpu-count max-wait-seconds opendashboard-node-host-memory-gb opendashboard-node-host-ocpu-count opensearch-cluster-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster update' = 'defined-tags display-name force freeform-tags from-json help if-match max-wait-seconds opensearch-cluster-id software-version wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster opensearch-cluster-collection list-opensearch-clusters' = 'all compartment-id display-name from-json help id lifecycle-state limit page page-size sort-by sort-order'
        'opensearch opensearch-cluster opensearch-versions-collection list-opensearch-versions' = 'all compartment-id from-json help limit page page-size'
        'opensearch opensearch-cluster work-request get' = 'from-json help work-request-id'
        'opensearch opensearch-cluster work-request-collection list-work-requests' = 'all compartment-id from-json help limit page page-size source-resource-id work-request-id'
        'opensearch opensearch-cluster work-request-error-collection list-work-request-errors' = 'all from-json help limit page page-size work-request-id'
        'opensearch opensearch-cluster work-request-log-entry-collection list-work-request-logs' = 'all from-json help limit page page-size work-request-id'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup delete' = 'force from-json help if-match max-wait-seconds opensearch-cluster-backup-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup get' = 'from-json help opensearch-cluster-backup-id'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup update' = 'defined-tags display-name force freeform-tags from-json help if-match max-wait-seconds opensearch-cluster-backup-id wait-for-state wait-interval-seconds'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup-collection list-opensearch-cluster-backups' = 'all compartment-id display-name from-json help id lifecycle-state limit page page-size sort-by sort-order source-opensearch-cluster-id'
    }
    return $ociCommandsToLongParams
}

function GetOciCommandsToShortParams_opensearch() {
    $ociCommandsToShortParams = @{
        'opensearch opensearch-cluster opensearch-cluster backup' = '? c h'
        'opensearch opensearch-cluster opensearch-cluster create' = '? c h'
        'opensearch opensearch-cluster opensearch-cluster delete' = '? h'
        'opensearch opensearch-cluster opensearch-cluster get' = '? h'
        'opensearch opensearch-cluster opensearch-cluster opensearch-cluster-restore' = '? c h'
        'opensearch opensearch-cluster opensearch-cluster resize-opensearch-cluster-horizontal' = '? h'
        'opensearch opensearch-cluster opensearch-cluster resize-opensearch-cluster-vertical' = '? h'
        'opensearch opensearch-cluster opensearch-cluster update' = '? h'
        'opensearch opensearch-cluster opensearch-cluster-collection list-opensearch-clusters' = '? c h'
        'opensearch opensearch-cluster opensearch-versions-collection list-opensearch-versions' = '? c h'
        'opensearch opensearch-cluster work-request get' = '? h'
        'opensearch opensearch-cluster work-request-collection list-work-requests' = '? c h'
        'opensearch opensearch-cluster work-request-error-collection list-work-request-errors' = '? h'
        'opensearch opensearch-cluster work-request-log-entry-collection list-work-request-logs' = '? h'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup delete' = '? h'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup get' = '? h'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup update' = '? h'
        'opensearch opensearch-cluster-backup opensearch-cluster-backup-collection list-opensearch-cluster-backups' = '? c h'
    }
    return $ociCommandsToShortParams
}