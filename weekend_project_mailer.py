__author__ = 'Joshua Braun'
__copyright__ = 'Copyright 2018, Joshua Braun'
__credits__ = ['Joshua Braun']
__license__ = ''
__version__ = '1.0.0'
__date__ = '05 Jan 2017'
__maintainer__ = 'Joshua Braun'
__email__ = 'jjabraun@gmail.com'
__status__ = 'Production'


class AirtableApi:
    def __init__(self, **kwargs):
        """
        Initialize Airtable API connection.
        :param kwargs['api_key']: API key, string
        :param kwargs['retry_sleep']: Retry sleep (seconds), integer
        :param kwargs['retry_count']: Retry count (number of attempts), integer
        """

        logging.debug('Initializing AirtableApi class.')
        self.api_key = kwargs.get('api_key')
        self.retry_sleep = kwargs.get('retry_sleep')
        self.retry_count = kwargs.get('retry_count')

    def _retrieve_table_json(self, base_id, table_name):
        """
        Retrieve table JSON.
        :param base_id: Base ID, string
        :param table_name: Table name, string
        :return: Table data, JSON object
        """

        import requests
        import json
        import urllib.parse
        from time import sleep

        logging.debug('Retrieving table "{0}".'.format(table_name))
        endpoint = 'https://api.airtable.com/v0/{0}/{1}?api_key={2}'.format(
            base_id,
            urllib.parse.quote(table_name, safe=''),
            self.api_key
        )
        for attempt in range(self.retry_count):
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error('Exception during GET from endpoint "{0}": "{1}".'.format(endpoint, e), exc_info=True)
                sleep(self.retry_sleep)
            else:
                logging.debug('GET finished successfully.')
                return json.loads(response.content)
        else:
            m = 'GET retried {0} times and failed.  Exiting.'.format(self.retry_count)
            logging.error(m)
            sys.exit(m)

    @staticmethod
    def _read_json_to_dataframe(input_json):
        """
        Read tabular data from JSON into a Pandas dataframe.
        :param input_json: Tabular data, JSON object
        :return: Tablular data, Pandas dataframe
        """

        from pandas.io.json import json_normalize

        logging.debug('Reading data from JSON into dataframe.')
        return json_normalize(input_json['records'])

    def return_table_as_dataframe(self, base_id, table_name):
        """
        Return the given Airtable as Pandas dataframe.
        :param base_id: Base ID, string
        :param table_name: Table name, string
        :return: Airtable data, Pandas dataframe.
        """

        logging.info('Returning Airtable "{0}" as dataframe.'.format(table_name))
        j = self._retrieve_table_json(base_id, table_name)
        return self._read_json_to_dataframe(j)


class Mailer:
    def __init__(self, **kwargs):
        """
        Initialize mail handler.
        :param kwargs['host']: SMTP host, string
        :param kwargs['port']: SMTP port, string
        :param kwargs['username']: Username, string
        :param kwargs['password']: Password, string
        :param kwargs['retry_sleep']: Retry sleep (seconds), integer
        :param kwargs['retry_count']: Retry count (number of attempts), integer
        """

        logging.debug('Initializing Mailer class.')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.retry_count = kwargs.get('retry_count')
        self.retry_sleep = kwargs.get('retry_sleep')

    def send_mail(self, sender, recipient_list, subject, message, high_priority=False):
        """
        Send mail.
        :param sender: Sender email address, string
        :param recipient_list: Recipient email addresses, list
        :param subject: Subject, string
        :param message: Message, string
        :param high_priority: Flag as high priority, Boolean
        :return: None
        """

        import smtplib
        from email.mime.text import MIMEText
        from time import sleep

        logging.info('Sending message with subject "{0}" to "{1}".'.format(subject, '", "'.join(recipient_list)))
        msg = MIMEText(message)
        msg['From'] = sender
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = subject
        if high_priority:
            msg['X-Priority'] = '2'
        for connect_attempt in range(self.retry_count):
            try:
                con = smtplib.SMTP(self.host, self.port)
                con.ehlo()
                con.starttls()
                con.ehlo()
                con.login(self.username, self.password)
            except smtplib.socket.gaierror as e:
                logging.error('SMTP connection failed: "{0}"'.format(e))
                sleep(self.retry_sleep)
            else:
                for send_attempt in range(self.retry_count):
                    try:

                        con.send_message(msg)
                    except smtplib.SMTPException as e:
                        logging.error('Send message failed: "{0}"'.format(e))
                        sleep(self.retry_sleep)
                    else:
                        con.quit()
                        break
                break


if __name__ == '__main__':
    import sys
    import os
    import argparse
    import configparser
    import logging

    from datetime import datetime
    from logging.handlers import TimedRotatingFileHandler

    # Parse arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-l', '--log',
        choices=['debug', 'info', 'warning', 'error'],
        default='info',
    )
    args = arg_parser.parse_args(sys.argv[1:])

    # Parse config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Instantiate logger
    logger = logging.getLogger()
    log_file = os.path.join('logs', '{0}.log'.format(os.path.splitext(os.path.basename(__file__))[0]))
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_file),
        when='midnight',
        backupCount=config['logger']['backup_count']
    )
    console_handler = logging.StreamHandler()
    logging.basicConfig(
        format='%(asctime)s\t%(levelname)s\t%(message)s',
        level=getattr(logging, args.log.upper()),
        handlers=[file_handler, console_handler]
    )
    logging.info('Script started.')

    # Only run on the given day of the week
    weekday_map = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6,
    }
    if datetime.now().weekday() != weekday_map[config['settings']['weekday'].lower()]:
        logging.info('Today isn\'t {0}.  Exiting.'.format(config['settings']['weekday']))
        sys.exit()

    # Retrieve Airtable data
    airtable = AirtableApi(
        api_key=config['airtable']['api_key'],
        retry_count=int(config['airtable']['retry_count']),
        retry_sleep=int(config['airtable']['retry_sleep']),
    )
    airtable_df = airtable.return_table_as_dataframe(config['airtable']['base_id'], config['airtable']['table_name'])

    # Create message
    logging.info('Creating message.')
    mail_message = '{0}\n\n'.format(config['settings']['message'])
    for do_soon in airtable_df.loc[airtable_df['fields.Do Soon'] == True]['fields.Project']:
        mail_message += '- {0}\n'.format(do_soon)
    for c in airtable_df['fields.Category'].unique():
        records_in_category = airtable_df.loc[airtable_df['fields.Category'] == c]
        incomplete_records = records_in_category[records_in_category['fields.Done'] != True]
        random_project = incomplete_records.sample()['fields.Project'].iloc[0]
        mail_message += '- {0}\n'.format(random_project)

    # Send mail
    mailer = Mailer(
        host=config['mailer']['host'],
        port=int(config['mailer']['port']),
        username=config['mailer']['username'],
        password=config['mailer']['password'],
        retry_count=int(config['mailer']['retry_count']),
        retry_sleep=int(config['mailer']['retry_sleep']),
    )
    mailer.send_mail(
        config['settings']['sender'],
        config['settings']['recipients'].split(','),
        config['settings']['subject'],
        mail_message,
    )
