from fuzzywuzzy import fuzz
import copy

from game.interpreters.state import State
from game.store.models.character import Abilities
import game.account_menu.menu

class SetCharacterStats(State):

    STATS = [
        'strength',
        'dexterity',
        'constitution',
        'intelligence',
        'wisdom',
        'willpower',
        'perception',
        'charisma'
    ]

    STAT_SHORT = {
        'strength': 'str',
        'dexterity': 'dex',
        'constitution': 'con',
        'intelligence': 'int',
        'wisdom': 'wis',
        'willpower': 'wil',
        'perception': 'per',
        'charisma': 'cha'
    }

    def __init__(self, player, store):
        self.current_stat = ''
        self.points = 200
        self.base_abilities = copy.copy(player.character.abilities)

        super(SetCharacterStats, self).__init__(player, store)



    def writeStats(self):
        character = self.player.character
        self.player.write("Str: %-2d Dex: %-2d Con: %-2d Int: %-2d Wis: %-2d Wil: %-2d Per: %-2d Cha: %-2d" % 
              (character.abilities.strength, character.abilities.dexterity, 
               character.abilities.constitution, character.abilities.intelligence, 
               character.abilities.wisdom, character.abilities.willpower, 
               character.abilities.perception, character.abilities.charisma))
        self.player.write("Points: %-3d" % self.points)

    def raiseStat(self, target):
        current = getattr(self.player.character.abilities, self.current_stat)
        base = getattr(self.base_abilities, self.current_stat)
        while current < target and current < base+10:
            cost = int((current - base)**1.25)
            if self.points - cost >= 0:
                self.points = self.points - cost
                current = current + 1
            else:
                break 
        setattr(self.player.character.abilities, self.current_stat, current) 

    def decreaseStat(self, target):
        current = getattr(self.player.character.abilities, self.current_stat)
        base = getattr(self.base_abilities, self.current_stat)
        while current > target and target >= base:
            current = current - 1
            cost = int((current - base)**1.25)
            self.points = self.points + cost
        setattr(self.player.character.abilities, self.current_stat, current) 

    def adjustStat(self, target):
        if target > getattr(self.player.character.abilities, self.current_stat):
            self.raiseStat(target)
        elif target < getattr(self.player.character.abilities, self.current_stat) \
                and target >= getattr(self.base_abilities, self.current_stat):
            self.decreaseStat(target)

    def findStat(self, stat):
        for s in self.STATS:
            if fuzz.partial_ratio(stat.lower(), s) == 100:
                return s
        return None

    def initializeCharacter(self):
        pass

    def resetCurrentStat(self):
        self.current_stat = ''
        self.player.setPrompt("stat> ")

    def introduction(self):
        self.writeStats()
        if not self.current_stat:
            self.player.setPrompt("stat> ")
        else:
            self.player.setPrompt(self.STAT_SHORT[self.current_stat] + "> ")

    def execute(self, input):
        try:
            stat, target = input.split(' ', 1)
        except ValueError:
            stat = input.strip()
            target = None 

        if stat == "done":
            self.initializeCharacter()
            self.player.character.save('data/characters/')
            self.player.account.addCharacter(self.player.character)
            self.player.character = None
            return account.menu.AccountMenu(self.player, self.store)

        if self.current_stat and stat.isdecimal():
            target = int(stat)
            self.adjustStat(target)
            self.resetCurrentStat()
            self.writeStats()
            return self

        if not target:
            stat = self.findStat(stat)
            if stat:
                self.current_stat = stat
                self.writeStats()
                self.player.setPrompt(self.STAT_SHORT[self.current_stat] + "> ")
            else: 
                self.player.write("That's not a stat you can adjust.")
            return self

        if target.isdecimal():
            stat = self.findStat(stat)
            if stat:
                self.current_stat = stat
                target = int(target)
                self.adjustStat(target)
                self.resetCurrentStat()
                self.writeStats()
            else:
                self.player.write("That's not a stat you can adjust.")

        return self
            

