# Automata Redis 
both for conventional key-value & timeseries data.

## Packaging
`python3 -m build`

## Commands
1. Timeseries Range (open ended) `TS.RANGE [KEY] 0 +`
2. Timeseries Range (latest value summarized) `TS.GET [KEY]`

## LXD Container

### Create LXD container
1. `cd ~/projects/scripts/bash-scripts/lxc/`
2. `./lxc-create-basic-ubuntu-container.sh automata-all 10.104.71.60 /projects/code/automata-projects/automata-deploy`
3. `lxc.list`

Add these aliases to `vi ~/bash/bash-profile-aliases/aliases/bash-projects`
```
# automata all
alias automata-all.lxc.start="lxc.start-container automata-all"
alias automata-all.lxc.stop="lxc.stop-container automata-all"
alias automata-all.lxc.run-in="lxc.run-in.container automata-all"
alias automata-all.project="cd ~/projects/code/automata-projects/automata-deploy"
```
Remember to run `source ~/.bashrc`

### Container Info
* `lxc image list images: ubuntu/22.04 amd64`

### Container Manipulation
* `lxc stop automata-all`
* `lxc delete automata-all`

### Accessing Container
* `automata-all.lxc.run-in`

## Redis (Container)

### Redis Install
1. `sudo apt update`
2. `sudo apt install redis`

### Redis Config
1. `sudo vi /etc/redis/redis.conf`
2. Change to `bind 10.104.71.60 127.0.0.1` (allow second IP for accessing on host by default)
3. `sudo systemctl restart redis-server`

## Redis Time Series

### Prerequisites
1. `sudo apt install make`
2. `sudo apt install python3-dev`

### Build & Install RedisTimeSeries Module
This is a module, which needs to be built, installed and configured into the Redis server.

1. `mkdir -p ~/software/redis/module`
2. `cd ~/software/redis/module`
3. `git clone --recursive https://github.com/RedisTimeSeries/RedisTimeSeries.git`
4. `cd ~/software/redis/module/RedisTimeSeries`
5. `make setup`
6. `make build`
7. `sudo mkdir /etc/redis/modules`
8. `sudo mv bin/linux-x64-release/redistimeseries.so /etc/redis/modules/` (get the actual file not symbolic linked one)
9. `sudo vi /etc/redis/redis.conf`
10. Add the line `loadmodule /etc/redis/modules/redistimeseries.so` to `redis.conf`

### Verify Redis log
`less /var/log/redis/redis-server.log` should see:

```
192:M 26 Jul 2022 13:00:44.751 * <timeseries> RedisTimeSeries version 999999, git_sha=7c671138969c9dd9edcd9825427a9d360ac147e7
192:M 26 Jul 2022 13:00:44.752 * <timeseries> Redis version found by RedisTimeSeries : 6.0.16 - oss
192:M 26 Jul 2022 13:00:44.755 * <timeseries> loaded default CHUNK_SIZE_BYTES policy: 4096
192:M 26 Jul 2022 13:00:44.755 * <timeseries> loaded server DUPLICATE_POLICY: block
192:M 26 Jul 2022 13:00:44.755 * <timeseries> Setting default series ENCODING to: compressed
192:M 26 Jul 2022 13:00:44.756 * <timeseries> Detected redis oss
192:M 26 Jul 2022 13:00:44.759 * Module 'timeseries' loaded from /etc/redis/modules/redistimeseries.so
```

### Verify via redis cli
1. `redis-cli`
2. `INFO Modules`

Should see:

```
# Modules
module:name=timeseries,ver=999999,api=1,filters=0,usedby=[],using=[],options=[]
```

### Redis Port (outside container)
* `nc -zv 10.104.71.60 6379`

Stop and start the container to ensure redis, has installed correctly.

## Backup (Redis)
1. `CONFIG get dir` (in `redis-cli`) Tells where the dump file is located
2. `SAVE`
3. `/var/lib/redis` (should be `dump.rdb`)
4. `sudo systemctl status redis-server`
5. `sudo systemctl stop redis-server`
6. `sudo cp /var/lib/redis/dump.rdb BACKUP-DIR`

## Restore (Redis)
1. `sudo systemctl stop redis-server`
2. `sudo cp BACKUP-DIR /var/lib/redis/dump.rdb`
3. `sudo systemctl start redis-server`