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
        # todo add docstring
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')  # todo needed?
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.retry_count = kwargs.get('retry_count')
        self.retry_sleep = kwargs.get('retry_sleep')

        self.send_mail(
            'jjabraun@gmail.com',
            'jjabraun@gmail.com',
            'test',
            'test',
        )

    def send_mail(self, sender, recipient_list, subject, message, high_priority=False):
        # todo add docstring
        import smtplib
        from email.mime.text import MIMEText
        from time import sleep

        msg = MIMEText(message)
        msg['From'] = sender
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = subject
        if high_priority:
            msg['X-Priority'] = '2'
        for connect_attempt in range(self.retry_count):
            try:
                s = smtplib.SMTP(self.host)
            except smtplib.socket.gaierror as e:
                sleep(self.retry_sleep)
            else:
                for send_attempt in range(self.retry_count):
                    try:
                        s.send_message(msg)
                    except smtplib.SMTPException as e:
                        sleep(self.retry_sleep)
                    else:
                        s.quit()
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

    # Send email
    mailer = Mailer(
        host=config['mailer']['host'],
        port=config['mailer']['port'],
        username=config['mailer']['username'],
        password=config['mailer']['password'],
        retry_count=int(config['mailer']['retry_count']),
        retry_sleep=int(config['mailer']['retry_sleep']),
    )
