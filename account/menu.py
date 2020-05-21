from interpreter.state import State
from interpreter.command import CommandInterpreter
from services.movement import MovementService

import account.password
import account.character.creation

class AccountMenu(State):

    ACCOUNT_MENU = """
==================== Account Menu ====================

menu                - Show this menu.
change password     - Set a new account password.

list                - List characters available to play.
play <name>         - Play a character.
create <name>       - Create a new character.

quit                - Leave the game.

======================================================
    """

    def introduction(self):
        self.player.setPrompt("> ")
        self.player.write(self.ACCOUNT_MENU, wrap=False)

    def execute(self, input):
        try:
            command, arguments = input.split(' ', 1)
        except ValueError:
            command = input.strip()
            arguments = ''

        if command == "menu":
            self.player.write(self.ACCOUNT_MENU, wrap=False)
            return self


        if command == "change" and arguments == "password":
            return account.password.GetNewAccountPassword(self.player, self.library)


        if command == "list":
            if not self.player.account.characters:
                self.player.write("There are no characters in your account yet!  Create one by typing `create <name>`.")
                return self

            self.player.write("You have the following characters in your account:\n")
            for name in self.player.account.characters:
                self.player.write("%s\n" % name.title())
            return self


        if command == "play":
            if arguments in self.player.account.characters:
                self.player.character = self.player.account.characters[arguments]
                self.player.character.player = self.player
                self.player.interpreter = CommandInterpreter(self.player, self.library)

                movement = MovementService()

                # If they aren't in the game world yet, send em to room 1.
                if not self.player.character.room:
                    movement.enter(self.player.character, self.library.rooms.getById(1))
                else:
                    movement.enter(self.player.character, self.player.character.room)

                self.player.write("Welcome back, %s!" % self.player.character.name.title())
                self.player.write(self.player.character.room.describe(self.player), wrap=False)
                return None

            self.player.write("You don't seem to have a character by that name.")
            return self 


        if command == "create":
            name = arguments
            if not name:
                self.player.write("You need to enter a name for the character you want to create.  Try `create <name>`.")
                return self

            if self.library.characters.hasId(name):
                self.player.write("A character with that name already exists.  Please try a different name.")
                return self

            self.player.character = self.library.characters.create(name)
            return account.character.creation.SetCharacterStats(self.player, self.library)
        

        if command == "quit":
            self.player.quit()
            return None
            
        self.player.write("That's not a menu option.")
        return self

# End AccountMenu

