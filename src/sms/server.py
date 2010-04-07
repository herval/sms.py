"""
SMS servers
"""
import glob
import logging
import os
import os.path
import subprocess
import sys
import sms

def incoming_server(device, incoming_directory, log_file):
    """
    Server entry point

    Writes incoming messages to files in a directory.
    Incoming message format:
      phone number
      date received in iso format (no tz)
      text message
    """
    # set up logging
    if log_file:
        logging.basicConfig(level=logging.DEBUG, 
                            filename = log_file, filemode='a',
                            format = 
                            '%(asctime)s %(name)s %(levelname)s %(message)s')
    logger = logging.getLogger('sms.server')

    # make sure directory exists
    if not os.path.exists(incoming_directory):
        os.makedirs(incoming_directory)
        logger.info('Created directory %s' % incoming_directory)

    # create modem
    m = sms.Modem(device)

    # ignore any existing messages
    ignore = [message.index for message in m.messages()]
    logger.debug('ignoring existing messages %s' % ignore)

    # message starting number
    n = 1
    for path in glob.iglob(os.path.join(incoming_directory, 'message*.txt')):
        try:
            num = int(path[7:-4])
            if num >= n:
                n = num + 1
        except ValueError:
            pass
    logger.debug('starting with message number %d' % n)

    print "waiting for incoming sms messages."
    print "will write messages to %s" % incoming_directory

    while True:
        logger.debug('began waiting')
        m.wait()
        logger.debug('wait done')
        for message in m.messages():
            if message.index in ignore:
                logger.debug('ignoring message %d' % message.index)
                continue
            filename = os.path.join(incoming_directory, 'message%d.txt' % n)
            f = open(filename, 'w')
            f.write('%s\n%s\n%s' % (message.number,
                                    message.date.isoformat(),
                                    message.text))
            f.close()
            n += 1
            logger.info('wrote incoming message: %s "%s"' % 
                        (filename, message))
            print "received a message. wrote it to %s" % filename
            message.delete()


def subprocess_server(device, args, log_file):
    """
    Server entry point

    This server launches a subprocess when a message is
    received. It sends the message to the program over stdin and waits
    for a response message on stdout.

    Incoming message format:
      phone number
      date received in iso format (no tz)
      text message

    Outgoing message format:
      phone number (should start with 1)
      text message
    """
    # set up logging
    if log_file:
        logging.basicConfig(level=logging.DEBUG, 
                            filename = log_file, filemode='a',
                            format = 
                            '%(asctime)s %(name)s %(levelname)s %(message)s')
    logger = logging.getLogger('sms.server')

    # create modem
    m = sms.Modem(device)

    # ignore any existing messages
    ignore = [message.index for message in m.messages()]
    logger.debug('ignoring existing messages %s', ignore)

    print "waiting for incoming sms messages."
    print "will pass messages to %s" % args

    while True:
        logger.debug('began waiting')
        m.wait()
        logger.debug('wait done')
        for message in m.messages():
            if message.index in ignore:
                logger.debug('ignoring message %d', message.index)
                continue
            logger.debug('received incoming message, launching process')
            p = subprocess.Popen(args, stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE)
            # get rid of new lines in message since the subprocess
            # expects the message to be only one line.
            text = message.text.strip()
            text = text.replace('\n', ' ')
            msg = '%s\n%s\n%s\n' % (message.number,
                                    message.date.isoformat(),
                                    message.text)
            message.delete()
            logger.debug('deleted incoming message')
            logger.debug('sending message to subprocess %s', msg)
            response = p.communicate(msg)[0]
            logger.debug('received response from subprocess %s', response)
            if response:
                try:
                    number, msg = response.split('\n', 1)
                except ValueError:
                    logger.error('malformed response: %s', response)
                    print "processed message, bad response"
                    continue
                m.send(number, msg)
                logger.info('sent response message %s %s', number, msg)
                print "processed message, sent response"
            else:
                logger.info('no response from subprocess')
                print "processed message, no response"

