Weekend Project Mailer
======================
Emails a selection of weekend projects from AirTable.

Configuration
-------------
Requires a config.ini file in the same directory as weekend_project_mailer.py in the following format:

[settings]
weekday: Saturday
sender: Email address
recipients: Email address(es)
subject: Email subject
message: Email message

[logger]
backup_count: 30

[airtable]
api_key: API key
retry_count: 5
retry_sleep: 30
base_id: Base ID
table_name: Table name

[mailer]
host: host
port: port
username: username
password: password
retry_count: 5
retry_sleep: 30
