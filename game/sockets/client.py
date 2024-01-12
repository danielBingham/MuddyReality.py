import telnetlib

###
# ClientSocket
# 
# A ClientSocker wrapper around python's native socket object.  Used to connect the socket to the
# server and to track inputs and outputs.  Manages a queue of input and a queue of output for the
# wrapped socket.
###


class ClientSocket:
    'A wrapper around the client socket.'

    ###
    # Constructor for the client socket.  Take a tuple as returned from ``socket.accept()`` and save
    # both the socket and address for later use.  Also take the parent server socket that accepted
    # the connection.
    ###
    def __init__(self, socket_tuple, server):
        socket, address = socket_tuple
        self.socket = socket
        self.address = address
        self.socket.setblocking(0)

        # This is the server socket that originated this client socket.  It will need to know if
        # this client closes, so that it can maintain its list.
        self.server = server

        # A queue of messages coming in.
        self.inputQueue = []

        # We'll use this to clear the output buffer.
        self.outputBufferReset = ""

        # A buffer of output to go out.
        self.outputBuffer = self.outputBufferReset 

        self.player = None

    def appendToOutputBuffer(self, output):
        self.outputBuffer += output

    def clearOutputBuffer(self):
        self.outputBuffer = self.outputBufferReset 
        return self

    ###
    # Is the output buffer empty?
    ###
    def outputBufferIsClear(self):
        return self.outputBuffer == self.outputBufferReset 

    ###
    # Do we have output that needs to be written?
    ###
    def hasOutput(self):
        return self.outputBuffer != self.outputBufferReset 

    def hasInput(self):
        return self.inputQueue

    def popInput(self):
        return self.inputQueue.pop()

    def disableEcho(self):
        seq = telnetlib.IAC + telnetlib.DONT + telnetlib.ECHO
        self.socket.send(seq)

    def enableEcho(self):
        seq = telnetlib.IAC + telnetlib.WILL + telnetlib.ECHO
        self.socket.send(seq)

    ###
    # Read whatever text currently exists on this socket, and place it in the Player's input queue,
    # where it can be processed by any command interpreters.
    ###

    def read(self):
        data = self.socket.recv(4096)
        if data:
            decoded = data.decode()
            self.inputQueue.append(decoded)
            if self.player:
                self.player.prompt.is_needed = True
        else:
            # We're in an error state.  Close down the socket.
            self.close()

    ###
    # Take the next batch of text from the player's output queue and write it out to the socket.
    ###

    def write(self):
        if self.hasOutput():
            self.socket.send(self.outputBuffer.encode())
            self.clearOutputBuffer()

            if self.player and self.player.prompt.is_in_buffer:
                self.player.prompt.is_needed = False 
                self.player.prompt.is_in_buffer = False
            elif self.player:
                self.player.is_needed = True

    ###
    # Handle any errors, closing the connection if necessary.
    ###
    def handleError(self):
        self.close() 

    ###
    # Close the connection to this socket
    ###
    def close(self):
        self.socket.close()
        self.server.remove(self)

    ###
    # Return the descriptor (file number) of the wrapped socket.  This way we can use our sockets
    # directly in ``select()`` and get them back, rather than having to do some sort of mapping
    # between the wrapped sockets and their parents.
    ###
    def fileno(self):
        return self.socket.fileno()


###
# End ClientSocket
###
