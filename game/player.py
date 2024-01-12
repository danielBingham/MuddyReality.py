from textwrap import TextWrapper


class Prompt:
    "A player's current prompt and methods necessary to set it."

    def __init__(self):

        # Does the player currently have a prompt in their output buffer?
        self.is_in_buffer = False

        # Does the player currently need a prompt?
        self.is_needed = True 

        # Is the player prompt currently turned off?
        self.is_off = False

        # Player's default prompt.
        self.default = "\n\n> "

        # Player's current prompt, initialized to the default.
        self.current = self.default


class Player:
    "A wrapper class for player data, used to track who is playing the game."

    wrapper = TextWrapper(width=80, replace_whitespace=False, initial_indent='', break_on_hyphens=False)

    STATUS_ACCOUNT = 'account'
    STATUS_GAME = 'game'

    def __init__(self, socket, account_interpreter, game_interpreter):
        """
        Initialize the player with their socket and references to interpreters.

        Parameters
        ----------
        socket: ClientSocket
            The player's client socket.
        account_interpreter:    StateInterpreter
            A reference to the interpreter used while the player is in the account flow.
        game_interpreter:   CommandInterpreter
            A reference to the interpreter used while the player is in the game.
        """

        # This is the player's client socket.
        self.socket = socket
        self.socket.player = self

        self.account_interpreter = account_interpreter
        self.game_interpreter = game_interpreter

        self.status = self.STATUS_ACCOUNT
        self.last_account_state = None
        self.current_account_state = None
        # Data that might need to be passed between states in the account flow.
        self.account_state_data = {}

        self.account = None
        self.character = None

        self.prompt = Prompt()

    def writePrompt(self):
        """
        Update the player's current prompt based on their character's state (if
        any) and then write it.
        """

        if self.character and self.character.action:
            self.prompt.is_off = True
        if self.prompt.is_needed and not self.prompt.is_off:
            if self.character:
                prompt = ""

                hunger = self.character.reserves.hungerString(True)
                if hunger:
                    if len(prompt) > 0:
                        prompt += ":"
                    prompt += hunger

                thirst = self.character.reserves.thirstString(True)
                if thirst:
                    if len(prompt) > 0:
                        prompt += ":"
                    prompt += thirst

                sleep = self.character.reserves.sleepString(True)
                if sleep:
                    if len(prompt) > 0:
                        prompt += ":"
                    prompt += sleep

                wind = self.character.reserves.windString(True)
                if wind:
                    if len(prompt) > 0:
                        prompt += ":"
                    prompt += wind

                energy = self.character.reserves.energyString(True)
                if energy:
                    if len(prompt) > 0:
                        prompt += ":"
                    prompt += energy

                prompt += "> "
                self.setPrompt(prompt)
            self.write(self.getPrompt(), wrap=False)
            self.prompt.is_in_buffer = True
            self.prompt.is_needed = False


    def setAccountState(self, state_string):
        """
        Set the current account state for players who are at the Account Menu.

        Parameters
        ----------
        state_string:   string
            The name of the state we want to set for the character.
        """

        if self.status != self.STATUS_ACCOUNT and state_string != None:
            raise ValueError("Can't set player account state when the player is in the game.")
        elif state_string != None:
            self.last_account_state = self.current_account_state
            self.current_account_state = state_string
            if self.last_account_state != self.current_account_state:
                self.account_interpreter.introduce(self)
        else:
            self.last_account_state = self.current_account_state
            self.current_account_state = None

    def interpret(self):
        """
        Interpret the player's input, using the interpreter appropriate to the
        player's current status.

        Raises
        ------
        RuntimeError
            If `Player.status` is set to an invalid value.
        """

        if self.hasInput():
            input = self.read().strip()

            # If we have input and the character is currently working on an
            # action, cancel the action.
            if self.character:
                if self.character.action:
                    self.character.action.cancel(self)
                    self.character.action = None
                    self.character.action_data = {}
                    self.character.action_time = 0
                    self.prompt_off = False

            # If we don't have input at this point, it means the player just sent
            # white space.  So we'll skip interpreting it and just send a new
            # prompt.
            if input:
                if self.status == self.STATUS_ACCOUNT:
                    self.account_interpreter.interpret(self, input)
                elif self.status == self.STATUS_GAME:
                    self.game_interpreter.interpret(self, input)
                else:
                    raise RuntimeError("Player status %s is invalid." % self.status)

    def quit(self):
        """
        Quit the game by closing the player's client socket.
        """

        self.socket.close()

    def hasInput(self):
        """
        Does the player currently have input waiting on their socket?

        Returns
        -------
        boolean:    True if there is input waiting in the socket.
        """

        return self.socket.hasInput()

    def write(self, text, wrap=True):
        """
        Write output to this player's client socket.

        Parameters
        ----------
        text:   string
            The text output we want to write to the socket.
        wrap:   boolean (Optional), Default: True
            Whether or not we should wrap the text to 80 characters.  Defaults
            to `True`.

        Returns
        Player: Returns the current player to allow chaining.
        """

        if wrap: 
            # Wrap will blow away any trailing white space. We want each call
            # to `write` to define a new line, however, so we need to add a
            # newline.
            text = self.wrapper.fill(str(text)) + "\n"

        # Add the output to the player output batch.  It will be send and
        # cleared in the next cycle.
        self.socket.appendToOutputBuffer(text)
        return self

    def read(self):
        """
        Read input from the player's client socket and return it.

        Returns
        -------
        string: The read input.
        """

        if self.socket.inputQueue:
            return self.socket.popInput()

    def getPrompt(self):
        """
        Get the current text prompt.

        Returns
        -------
        string: The player's current prompt.
        """

        return self.prompt.current

    def setPrompt(self, prompt):
        """
        Set the player's current text prompt.

        Parameters
        ----------
        prompt: string
            The text to set the prompt to.

        Returns
        -------
        Player: Returns `self` to allow chaining.
        """

        self.prompt.current = "\n\n" + prompt
        self.prompt.is_in_buffer = False
        return self

    # Currently unimplemented.  They had buggy behavior that I haven't gotten
    # around to debugging.
    #
    # TODO Debug these so that we can turn off echo while taking passwords.
    def disableEcho(self):
        # self.socket.disableEcho()
        pass

    def enableEcho(self):
        # self.socket.enableEcho()
        pass
