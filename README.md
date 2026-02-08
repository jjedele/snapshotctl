# snapshotctl

A simple CLI tool for managing filesystem snapshots across BTRFS and ZFS volumes.

## Configuration

snapshotctl reads its configuration from `/etc/snapshots.conf`. The file uses INI-style sections, one per volume:

```ini
[volume.root]
type = btrfs
location = /mnt/btrfs_root/@
snapshot_destination = /snapshots

[volume.data]
type = zfs
location = datapool/data
```

### Volume options

| Option                 | Required | Applies to | Description                                  |
|------------------------|----------|------------|----------------------------------------------|
| `type`                 | yes      | all        | Filesystem type (`btrfs` or `zfs`)           |
| `location`             | yes      | all        | Subvolume path (BTRFS) or dataset name (ZFS) |
| `snapshot_destination` | yes      | btrfs      | Directory to store BTRFS snapshots in        |

ZFS snapshots are stored inline on the dataset, so no `snapshot_destination` is needed.

## Usage

```
snapshotctl <command>
```

### Commands

- **`snapshot`** -- Create a new snapshot for every configured volume. Snapshots are named with a `YYYYMMDDTHHMMSS` timestamp.
- **`list`** -- List existing snapshots for every configured volume.

### Examples

```sh
# Create snapshots for all configured volumes
sudo snapshotctl snapshot

# List all snapshots
sudo snapshotctl list
```

## Snapshot naming

- **BTRFS**: `<sanitized_location>_<timestamp>` stored under `snapshot_destination` (e.g. `/snapshots/mnt_btrfs_root_@_20260208T140000`).
- **ZFS**: `<dataset>@<timestamp>` (e.g. `datapool/data@20260208T140000`).
