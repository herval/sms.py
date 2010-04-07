SMS
===

The sms package provides sms capabilities for Enfora gsm modems, and
probably others. I developed this package for my location-specific
nature haiku by sms project N8R TXT (http://n8rtxt.org/).

The sms package provides Modem and Message classes for sending and
receiving sms message.

The `sms.server` module provides two servers that allow you to
dispatch incoming sms messages. The `sms.echo` module is an example
that works with the `sms.server.subprocess_server`.

Usage
-----

Create a modem object passing it the serial device ID. On windows this
would be something like 'COM1'. The example below is for mac and
linux:

    >>> import sms
    >>> m = sms.Modem('/dev/ttyS0')

You can have use several modem objects concurrently if you have more
than one modem attached to different serial ports.

To send a sms message call the send method, passing a phone number
string and a message string.

    >>> m.send('14161234567', 'This is a message')

If an error occurs a ModemError will be raised with the error message.

    >>> m.send('14161234567', 'This is a message')
    Traceback (most recent call last):
    ...
    ModemError: ['ERROR']

You can retrieve sms messages with the messages() method. It returns a
sequence of message objects.

    >>> m.messages()
    [<sms.Message object at 0x...>]

Message objects have a couple attributes: number, date, and text.

    >>> msgs = m.messages()
    >>> msgs[0].number
    '+16476186676'

    >>> msgs[0].date
    datetime.datetime(2008, 7, 11, 11, 2, 11)

    >>> msgs[0].text
    'Activation code 63966 Go 2 www.ipipi.com and signin with  your username and pwd, enter 63966 to activate your mobile/account\n\nWelcome 2 ipipi.com'

After you receive messages you'll want to delete them from the SIM
card. This is done by calling the delete method on the messages.

    >>> msgs[0].delete()

Rather than polling the modem to find messages you can call the wait()
method, which blocks until a message is received. The wait method
takes an optional timeout argument.

    >>> m.wait(1) # waiting with 1 timeout

    >>> m.wait() # waiting with no timeout

The wait message doesn't return anything. You should call the
messages() method after it returns to receive the messages. Note that
it's possible that there may in fact be no messages available after
the wait method returns.
