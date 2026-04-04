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
| `retention`            | no       | all        | Retention policy for the `sync` command (see below) |

ZFS snapshots are stored inline on the dataset, so no `snapshot_destination` is needed.

### Retention policy

The `retention` option defines how many snapshots to keep at each granularity level. It is a space-separated string of `<count><unit>` pairs:

| Unit | Meaning | Description                              |
|------|---------|------------------------------------------|
| `h`  | hourly  | Keep one snapshot per hour               |
| `d`  | daily   | Keep one snapshot per day                |
| `w`  | weekly  | Keep one snapshot per week               |
| `m`  | monthly | Keep one snapshot per month              |

For example, `"24h 7d 4w 12m"` means: keep the latest snapshot from each of the last 24 hours, 7 days, 4 weeks, and 12 months. Older snapshots outside these windows are deleted.

Volumes without a `retention` value are skipped by the `sync` command.

## Usage

```
snapshotctl <command>
```

### Commands

- **`snapshot`** -- Create a new snapshot for every configured volume. Snapshots are named with a `YYYYMMDDTHHMMSS` timestamp.
- **`sync`** -- Create a new snapshot and then prune outdated snapshots according to each volume's `retention` policy. Volumes without a `retention` value are skipped.
- **`list`** -- List existing snapshots for every configured volume.

### Examples

```sh
# Create snapshots for all configured volumes
sudo snapshotctl snapshot

# Create snapshots and prune old ones per retention policy
sudo snapshotctl sync

# List all snapshots
sudo snapshotctl list
```

## Snapshot naming

- **BTRFS**: `<sanitized_location>_<timestamp>` stored under `snapshot_destination` (e.g. `/snapshots/mnt_btrfs_root_@_20260208T140000`).
- **ZFS**: `<dataset>@<timestamp>` (e.g. `datapool/data@20260208T140000`).
