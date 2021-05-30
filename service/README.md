# Sync Sbanken transactions to YNAB as a service
Sbanken to YNAB may be run as a service rather than using cron

To make that happen, modify and then copy the files in the ./service folder:

`sbanken-sync.service`

`sbanken-sync.timer`

## Setting up the sync Service
In `sbanken-sync.service` change 
After modifying the `sbanken-sync.service` file, copy it to `/etc/systemd/system` using root.:
```
$ sudo cp  sbanken-sync.service /etc/systemd/system/sbanken-sync.service
```

## Setting up the schedule
Edit `sbanken-sync.timer` particularly focus on 
```
[Timer]
OnCalendar=*-*-* 01:00:00
```
Set this to a value that suits you. The default runs the service at one in the morning every day. Changing to
```
OnCalendar=Hourly 
```
will run the sync every hour - on the hour. Script should be capable to handle this.
See also https://wiki.archlinux.org/title/Systemd/Timers for more options.

After modifying the `sbanken-sync.timer` file, copy it to `/etc/systemd/system` using root.:
```
$ sudo cp  sbanken-sync.timer /etc/systemd/system/sbanken-sync.timer
```

Start the sync timer running:
```
$ sudo systemctl start sbanken-sync.timer
```

To verify that your timer is scheduled to run sync, use the command:
```
$ systemctl list-timers
```
or check the run status:
```
$ sudo systemctl status sbanken-sync.timer
```
