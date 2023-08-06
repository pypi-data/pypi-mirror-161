#!/usr/bin/env python
# coding: utf-8

# Newport Oriel Monochromator
# For use with a Oriel Cornerstone 260 monochromator.
# For documentation see the [Oriel Cornerstone Manual](https://www.newport.com/medias/sys_master/images/images/hae/h47/8797226926110/Oriel-Cornerstone-260-User-Manual-RevA.pdf).

<<<<<<< HEAD

=======
from typing import Dict, Union
>>>>>>> dev
import serial
from collections import namedtuple


<<<<<<< HEAD
Response = namedtuple( 'Response', [ 'statement', 'response' ] )
=======
Response = namedtuple('Response', ['statement', 'response'])
>>>>>>> dev


class Monochromator:
    """
    Represents an Oriel Cornerstone 260 monochromator.
    """

<<<<<<< HEAD
    def __init__( self, port, timeout = 5 ):
=======
    def __init__(self, port: str, timeout: int = 5):
>>>>>>> dev
        """
        Creates a new Monochromator.

        :param port: Device port.
        :param timeout: Communication timeout.
        """
        self.port = port
        self.term_chars = '\r\n'
        self.encoding = 'utf-8'
<<<<<<< HEAD
        self._com = serial.Serial( port, timeout = timeout )


    def __del__( self ):
=======
        self._com = serial.Serial(port, timeout = timeout)


    def __del__(self):
>>>>>>> dev
        """
        Closes serial port connection.
        """
        self._com.close()


<<<<<<< HEAD
    def __getattr__( self, attr ):
=======
    def __getattr__(self, attr: str):
>>>>>>> dev
        """
        Pass unknown attributes to serial.

        :param attr: Attribute.
        """
<<<<<<< HEAD
        return getattr( self._com, attr )
=======
        return getattr(self._com, attr)
>>>>>>> dev


    #--- low level methods ---


<<<<<<< HEAD
    def connect( self ):
=======
    def connect(self):
>>>>>>> dev
        """
        Connects to the device.
        """
        self._com.open()


<<<<<<< HEAD
    def disconnect( self ):
=======
    def disconnect(self):
>>>>>>> dev
        """
        disconnects from the device.
        """
        self._com.close()


<<<<<<< HEAD
    def write( self, msg ):
=======
    def write(self, msg: str) -> int:
>>>>>>> dev
        """
        Writes a message to the monochromator.

        :param msg: Message to send.
        :returns: Number of bytes written.
        """
        msg += self.term_chars
        msg = msg.upper()
<<<<<<< HEAD
        msg = msg.encode( self.encoding )
        return self._com.write( msg )


    def read( self ):
=======
        msg = msg.encode(self.encoding)
        return self._com.write(msg)


    def read(self) -> str:
>>>>>>> dev
        """
        Reads the buffer of the monochromator.

        :returns: The response.
        """
        resp = self._com.read_until(self.term_chars.encode(self.encoding))
        resp = resp.decode(self.encoding)
        return resp


<<<<<<< HEAD
    def command( self, cmd, *args ):
=======
    def command(self, cmd: str, *args) -> str:
>>>>>>> dev
        """
        Sends a command to the monochromator.

        :param msg: Message to send.
        :returns: Command sent.
        """
<<<<<<< HEAD
        args = map( str, args )
        msg = cmd + ' ' +  ' '.join( args )

        self.write( msg )
        return self.read().rstrip()


    def query( self, msg ):
        """
        Queries the monochromator.
        Equivalent to doing a write( msg ) then a read().
=======
        args = map(str, args)
        msg = cmd + ' ' +  ' '.join(args)

        self.write(msg)
        return self.read().rstrip()


    def query(self, msg: str) -> Response:
        """
        Queries the monochromator.
        Equivalent to doing a write(msg) then a read().
>>>>>>> dev

        :param msg: Query message. '?' added if needed.
        :returns: A dictionary object containing the statement and response.
        """
        if msg[-1] != '?':
            msg += '?'

<<<<<<< HEAD
        self.write( msg )

        statement = self.read().rstrip()
        response  = self.read().rstrip()
        return Response( statement = statement, response = response )
=======
        self.write(msg)

        statement = self.read().rstrip()
        response  = self.read().rstrip()
        return Response(statement = statement, response = response)
>>>>>>> dev


    #--- high level methods ---


    @property
    def info(self) -> str:
        """
        :returns: Device info.
        """
        resp = self.query('info')
        return resp.response


    @property
    def position(self) -> float:
        """
        :returns: Current wavelength position in nanometers.
        """
        resp = self.query('wave')
        resp = resp.response
<<<<<<< HEAD
        return float( resp )


    def step( self, steps ):
=======
        return float(resp)


    def step(self, steps: int):
>>>>>>> dev
        """
        Moves the monochromator a given number of steps.

        :param steps: Number of steps to move.
        """
<<<<<<< HEAD
        self.command( 'step', steps )


    def goto( self, wavelength ):
=======
        self.command('step', steps)


    def goto(self, wavelength: float) -> float:
>>>>>>> dev
        """
        Moves monochromator to given wavelength.

        :param wavelength: Desired wavelength in nanometers.
        :returns: Set wavelength.
        """
<<<<<<< HEAD
        wavelength = '{:.3f}'.format( wavelength )
        self.command( 'gowave', wavelength )
=======
        wavelength = f'{wavelength:.3f}'
        self.command('gowave', wavelength)
>>>>>>> dev

        return self.position


<<<<<<< HEAD
    def abort( self ):
=======
    def abort(self):
>>>>>>> dev
        """
        Halts the monochromator.
        """
<<<<<<< HEAD
        self.command( 'abort' )
=======
        self.command('abort')
>>>>>>> dev


    @property
    def grating(self) -> Dict[str, Union[str, int]]:
        """
        :returns: Current grating's properties.
            Dictionary with keys ['number', 'lines', 'label'].
        """
        resp = self.query('grat')
        resp = resp.response.split(',')
        return {
            'number': int(resp[0]),
            'lines':  int(resp[1]),
            'label':  resp[2]
        }


<<<<<<< HEAD
    def set_grating( self, grating ):
=======
    def set_grating(self, grating: int):
>>>>>>> dev
        """
        Sets the grating.

        :param grating: Number of the grating.
        """
<<<<<<< HEAD
        self.command( 'grat', str( grating ) )


    @property
    def shuttered( self ):
        """
        :returns: True if shutter is close , False if open
        """
        resp = self.query( 'shutter' )
        return ( resp.response == 'C' )


    def shutter( self, close = True ):
=======
        self.command('grat', grating)


    @property
    def filter(self) -> int:
        """
        :returns: Current filter position.
        """
        resp = self.query('filter')
        resp = resp.response
        return int(resp)
    

    def set_filter(self, pos: int):
        """
        Sets the filter to the given position.

        :param filter: Filter position to move to.
        """
        self._validate_filter(pos)
        self.command('filter', pos)


    def filter_label(self, filter: int, label: Union[None, str] = None) -> str:
        """
        Gets or sets a filter's label.

        :param filter: Number of the filter.
        :param label: If None, gets the filter's label.
            Otherwise, the label to assign.
        :returns: The filter's current label.
        :raises ValueError: If label is invalid.
        """
        self._validate_filter()
        cmd = f'filter{filter}label'

        if label is not None:
            if len(label) > 8:
                raise ValueError('Label is too long, must be less than 9 characters.')
            
            self.command(cmd, label)
            
        resp = self.query(cmd)
        return resp.response


    @property
    def shuttered(self) -> bool:
        """
        :returns: True if shutter is close , False if open
        """
        resp = self.query('shutter')
        return (resp.response == 'C')


    def shutter(self, close: bool = True):
>>>>>>> dev
        """
        Opens or closes the shutter.

        :param close: True to close the shutter, False to open.
            [Default: True]
        """
        cmd = 'C' if close else 'O'
<<<<<<< HEAD
        self.command( 'shutter', cmd )
=======
        self.command('shutter', cmd)
>>>>>>> dev


    @property
    def outport(self) -> int:
        """
        :returns: The output port number.
        """
<<<<<<< HEAD
        resp = self.query( 'outport' )
        return int( resp.response )


    def set_outport( self, port ):
=======
        resp = self.query('outport')
        return int(resp.response)


    def set_outport(self, port: int):
>>>>>>> dev
        """
        Sets the ouput port.

        :param port: Output port to set.
        """
<<<<<<< HEAD
        self.command( 'outport', str( port ) )


    def slit_width( self, slit, width = None ):
        """
        Gets or sets the slit with.
=======
        self.command('outport', port)


    def slit_width(self, slit: int, width: Union[int, None] = None) -> int:
        """
        Gets or sets the slit width.
>>>>>>> dev

        :param slit: Slit number.
        :param width: If None, returns current slit width.
            If a number, sets the slit width in microns.
            [Default: None]
        :returns: Slit width in microns.
        """
        cmd = f'slit{slit}microns'
        if width is not None:
<<<<<<< HEAD
            self.command( cmd, str( width ) )

        resp = self.query( cmd )
        return int( resp.response )
=======
            self.command(cmd, width)

        resp = self.query(cmd)
        return int(resp.response)


    @staticmethod
    def _validate_filter(pos: int) -> bool:
        """
        Validates a filter position.

        :param pos: Filter position to validate.
        :returns: True if filter position is valid.
        :raises ValueError: If filter position is invalid.
        """
        MIN_VAL = 1
        MAX_VAL = 6

        if (pos < MIN_VAL) or (pos > MAX_VAL):
            raise ValueError(f'Invalid filter value. Must be between {MIN_VAL} and {MAX_VAL}.')
        
        return True
>>>>>>> dev
