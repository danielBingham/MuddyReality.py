from game.interpreters.state.state import State


class AccountMenu(State):
    """
    Present the player with the account menu and then execute their account commands.
    """

    NAME = "account-menu"
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

    def introduce(self, player):
        "See State::introduce()"

        player.setPrompt("> ")
        player.write(self.ACCOUNT_MENU, wrap=False)

    def execute(self, time, player, input):
        "See State::execute()"

        try:
            command, arguments = input.split(' ', 1)
        except ValueError:
            command = input.strip()
            arguments = ''

        if command == "menu":
            player.write(self.ACCOUNT_MENU, wrap=False)
            return self.NAME

        if command == "change" and arguments == "password":
            return "get-new-account-password" 

        if command == "list":
            if not player.account.characters:
                player.write("There are no characters in your account yet!  Create one by typing `create <name>`.")
                return self.NAME

            player.write("You have the following characters in your account:\n")
            for name in player.account.characters:
                player.write("%s\n" % name.title())
            return self.NAME

        if command == "play":
            if arguments.lower() in player.account.characters:
                player.character = player.account.characters[arguments.lower()]
                player.character.player = player
                player.status = player.STATUS_GAME

                # If they aren't in the game world yet, send em to room 1.
                if not player.character.room:
                    self.library.movement.enter(player.character, self.store.rooms.getById(1))
                else:
                    self.library.movement.enter(player.character, player.character.room)

                player.write("Welcome back, %s!" % player.character.name.title())
                player.write(player.character.room.describe(player), wrap=False)
                return None

            player.write("You don't seem to have a character by that name.")
            return self.NAME 

        if command == "create":
            name = arguments
            if not name:
                player.write("You need to enter a name for the character you want to create.  Try `create <name>`.")
                return self.NAME

            if self.store.characters.hasId(name):
                player.write("A character with that name already exists.  Please try a different name.")
                return self.NAME

            player.character = self.store.characters.create(name)
            self.store.saveCharacter(player.character)
            player.account.addCharacter(player.character)
            player.character = None

            return self.NAME 

        if command == "quit":
            player.quit()
            return None

        player.write("That's not a menu option.")
        return self.NAME


