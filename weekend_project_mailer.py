__author__ = 'Joshua Braun'
__copyright__ = 'Copyright 2018, Joshua Braun'
__credits__ = ['Joshua Braun']
__license__ = ''
__version__ = '1.0.0'
__date__ = '05 Jan 2017'
__maintainer__ = 'Joshua Braun'
__email__ = 'jjabraun@gmail.com'
__status__ = 'Development'


class AirtableApi:
    def __init__(self, **kwargs):
        pass


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

        logging.debug('Mailer class instantiated.')
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

        logging.debug('Sending message with subject "{0}" to "{1}".'.format(subject, '", "'.join(recipient_list)))
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

    # todo get data
    # todo add unit tests, for practice

    # Send mail
    mailer = Mailer(
        host=config['mailer']['host'],
        port=int(config['mailer']['port']),
        username=config['mailer']['username'],
        password=config['mailer']['password'],
        retry_count=int(config['mailer']['retry_count']),
        retry_sleep=int(config['mailer']['retry_sleep']),
    )
