# Jack - Railway without Redis

Redis has been removed from the normal startup. `localdb.py` provides the Redis
operations used by the plugins using SQLite.

## Railway variables
- `BOT_TOKEN` = Telegram bot token
- `OWNER_ID` = your numeric Telegram user ID
- `API_ID` = optional
- `API_HASH` = optional
- `LOCAL_DB_PATH` = optional, defaults to `jack.db`

Start command: `python main.py`

For persistent SQLite data after redeploys, attach a Railway Volume and point
`LOCAL_DB_PATH` to a file on that volume.
