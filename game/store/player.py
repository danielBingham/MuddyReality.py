from textwrap import TextWrapper

############
# Player
#
# A class to wrap player data, used to track who's connected to the server.
###########


class Player:
    'A wrapper class for player data, used to track who is playing the game.'

    wrapper = TextWrapper(width=80, replace_whitespace=False, initial_indent='', break_on_hyphens=False)

    def __init__(self, socket):
        self.socket = socket
        self.socket.player = self

        self.interpreter = None 
        self.account = None
        self.character = None

        self.promptInBuffer = False
        self.need_prompt = True 
        self.prompt_off = False

        self.defaultPrompt = "\n\n> "
        self.prompt = self.defaultPrompt

    def quit(self):
        self.socket.close()
 
    def interpret(self):
        input = self.read().strip()

        # If we don't have input at this point, it means the player just sent white space.  So we'll
        # skip interpreting it and just send a new prompt.
        if input:
            self.interpreter.interpret(input)
        
        #if not self.hasPromptInBuffer():
        #    self.write(self.getPrompt(), wrap=False)
        #    self.setPromptInBuffer(True)

    def hasInput(self):
        return self.socket.hasInput()

    def write(self, text, wrap=True):
        if wrap: 
            # Wrap will blow away any trailing white space. We want each call to `write` to define a
            # new line, however, so we need to add a newline.
            text = self.wrapper.fill(str(text)) + "\n"

        # Add the output to the player output batch.  It will be send and cleared in the next cycle.
        self.socket.appendToOutputBuffer(text)
        return self

    def read(self):
        if self.socket.inputQueue:
            return self.socket.popInput()

    def hasPromptInBuffer(self):
        return self.promptInBuffer

    def setPromptInBuffer(self, promptInBuffer):
        self.promptInBuffer = promptInBuffer 
        return self

    def getPrompt(self):
        return self.prompt

    def setPrompt(self, prompt):
        self.prompt = "\n\n" + prompt
        self.setPromptInBuffer(False)
        return self

    def setDefaultPrompt(self):
        self.prompt = self.defaultPrompt
        self.setPromptInBuffer(False)
        return self

    def disableEcho(self):
        #self.socket.disableEcho()
        pass

    def enableEcho(self):
        #self.socket.enableEcho()
        pass

## End Player
