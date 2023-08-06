from grid.sdk.datastores import DATASTORE_FSX_THROUGHPUT_ALIASES
from grid.cli.observables.base import create_table
from grid.sdk.datastores import Datastore


def datastore_uploaded_info_table(dstore: Datastore):

    table_dict = {
        'Name': dstore.name,
        'Cluster ID': dstore.cluster_id,
        'Version': str(dstore.version),
        'Size': str(dstore.size),
        'Created At': f'{dstore.created_at:%Y-%m-%d %H:%M}'
    }
    if dstore._fsx_enabled:
        fsx_throughput_mbs_tib = dstore._fsx_throughput_mbs_tib
        fsx_capacity = dstore._fsx_capacity_gib
        fsx_throughput_alias = {v: k
                                for k, v in DATASTORE_FSX_THROUGHPUT_ALIASES.items()}.get(fsx_throughput_mbs_tib, "")

        table_dict.update({
            'HPD Throughput': f'{fsx_throughput_alias} ({fsx_throughput_mbs_tib}MB/s/TiB)',
            'HPD Capacity': f'{fsx_capacity}GiB',
            'Total Throughput': f'{fsx_throughput_mbs_tib * fsx_capacity / 1000}MB/s'
        })

    table = create_table([key for key, value in table_dict.items() if value is not None])
    table.add_row(*[value for value in table_dict.values() if value is not None])

    return table
