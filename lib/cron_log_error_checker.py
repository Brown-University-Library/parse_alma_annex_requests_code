"""
Script to check current `parse_alma_annex_requests.log` file for an error.
If an error is found, an email is sent.
Called by cron-job, like (pseudocode)...
- $ cd to parse_alma_annex_requests_code
- $ source ../env/bin/activate
- $ python3 ./lib/cron_log_error_checker.py
"""

import datetime, json, logging, os, pprint, smtplib
from email.mime.text import MIMEText


logging.basicConfig(
    level = os.environ['ANX_ALMA__LOGFILE_ERROR_EMAIL_LOGLEVEL'],  # set to 'WARNING' in production to only generate output on an error that will trigger and email, by crontab, to crontab owner significant failure.
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)


EMAIL_FROM = os.environ['ANX_ALMA__LOGFILE_ERROR_EMAIL_FROM']
EMAIL_HOST = os.environ['ANX_ALMA__LOGFILE_ERROR_EMAIL_HOST']
EMAIL_PORT = os.environ['ANX_ALMA__LOGFILE_ERROR_EMAIL_PORT']
EMAIL_RECIPIENTS = json.loads( os.environ['ANX_ALMA__LOGFILE_ERROR_EMAIL_RECIPIENTS_JSON'] )
LOG_FILEPATH = os.environ['ANX_ALMA__LOGFILE_PATH']  # different from `ANX_ALMA__LOG_PATH` for testing convenience


def _search_for_errors():
    """ Checks active log-file for error entries.
        Called by run_check() """
    ( error_lines, err ) = ( [], '' )
    try:
        with open( LOG_FILEPATH, 'r' ) as f:
            for line in f:
                if '] ERROR [' in line:
                    error_lines.append( line )
    except Exception as e:
        err = repr(e)
    log.debug( f'initial error_lines, ``{pprint.pformat(error_lines)}``' )
    if error_lines:
        error_lines[-4:]
    log.debug( f'err, ``{err}``' )
    return ( error_lines, err )


def _send_mail( message ):
    """ Sends mail; generates exception which cron-job should email to crontab owner on sendmail failure.
        Called by run_check() """
    log.debug( f'message, ``{message}``' )
    try:
        s = smtplib.SMTP( EMAIL_HOST, EMAIL_PORT )
        body = f'datetime: `{str(datetime.datetime.now())}`\n\nlast few error-entries...\n\n{message}\n\nLog path: `{LOG_FILEPATH}`\n\n[END]'
        eml = MIMEText( f'{body}' )
        eml['Subject'] = 'error found in parse-alma-exports logfile'
        eml['From'] = EMAIL_FROM
        eml['To'] = ';'.join( EMAIL_RECIPIENTS )
        s.sendmail( EMAIL_FROM, EMAIL_RECIPIENTS, eml.as_string())
    except Exception as e:
        err = repr( e )
        log.exception( f'Problem sending mail, ``{err}``' )
    return


def run_check( path ):
    ( error_lines, err ) = _search_for_errors()
    assert type(error_lines) == list; assert type(err) == str
    if len(error_lines) > 0:
        log.debug( 'sending email re log-errors' )
        recent_errors = error_lines[-4:]
        message = f'%s' % pprint.pformat(recent_errors)
        _send_mail( message )
    elif len(err) > 0:
        log.debug( 'sending email re log-search issue' )
        message = err
        _send_mail( message )
    else:
        log.debug( 'not sending email' )
    return


if __name__ == '__main__':
    try:
        run_check( path=LOG_FILEPATH )
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem running log error-check, ``{err}``' )
