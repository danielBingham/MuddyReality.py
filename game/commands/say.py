from interpreter.command import Command

class Say(Command):
    'Say something to the room.'

    def execute(self, player, arguments):
        for p in self.library.players:
            if p == player:
                p.write('You say "%s"' % (arguments))
            else:
                p.write('%s says "%s"' % (player.account.name, arguments))

