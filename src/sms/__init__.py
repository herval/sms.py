import datetime
import logging
import re
import serial


pat = re.compile(r'\+CMGL: (?P<index>\d+),'
                 '"(?P<status>.+?)",'
                 '"(?P<number>.+?)",'
                 '("(?P<name>.+?)")?,'
                 '("(?P<date>.+?)")?\r\n'
                 )

logger = logging.getLogger('sms.modem')

class ModemError(RuntimeError):
    pass


class Message(object):
    """A received SMS message"""

    format = '%y/%m/%d,%H:%M:%S'

    def __init__(self, index, modem, number, date, text):
        self.index = index
        self.modem = modem
        self.number = number
        if date is not None:
            # modem incorrectly reports UTC time rather than local
            # time so ignore time zone info
            date = date[:-3]
            self.date = datetime.datetime.strptime(date, self.format)
        self.text = text

    def delete(self):
        self.modem._command('AT+CMGD=%d' % self.index)


class Modem(object):
    """Provides access to a gsm modem"""
    
    def __init__(self, dev_id):
        self.conn = serial.Serial(dev_id, 9600, timeout=.5, rtscts=1)
        # make sure modem is OK
        self._command('AT')
        self._command('AT+CMGF=1') # set modem into text mode

    def send(self, number, message):
        """Send a SMS message

        number should start with 1
        message should be no more than 160 ASCII characters.
        """
        self._command('AT+CMGS="%s"' % number)
        self._command(message + '\x1A', flush=False)

    def messages(self):
        """Return received messages"""
        msgs = []
        text = None
        index = None
        date = None
        self._command('AT+CPMS="SM"') # read from memory TODO specify a different storage
        self._command("AT+CPMS=?")
        self._command("AT+CMGL=?")
        for line in self._command('AT+CMGL="ALL"')[:-1]:
            m = pat.match(line)
            if m is not None:
                if text is not None:
                    msgs.append(Message(index, self, number, date, text))
                status = m.group('status')
                index = int(m.group('index'))
                number = m.group('number')
                date = m.group('date')
                text = ''
            elif text is not None:
                if line == '\r\n':
                    text += '\n'
                else:
                    text += line.strip()
        if text is not None:
            msgs.append(Message(index, self, number, date, text))
        return msgs
    
    def wait(self, timeout=None):
        """Blocking wait until a message is received or timeout (in secs)"""
        old_timeout = self.conn.timeout
        self.conn.timeout = timeout
        results = self.conn.read()
        logger.debug('wait read "%s"' % results)
        self.conn.timeout = old_timeout
        results = self.conn.readlines()
        logger.debug('after wait read "%s"' % results)
        
    def _command(self, at_command, flush=True):
        logger.debug('sending "%s"' % at_command)
        self.conn.write(at_command)
        if flush:
            self.conn.write('\r\n')
            logger.debug('sending crnl')
        results = self.conn.readlines()
        logger.debug('received "%s"' % results)
        for line in results:
            if 'ERROR' in line:
                raise ModemError(results)
        return results
    
    def __del__(self):
        try:
            self.conn.close()
        except AttributeError:
            pass
