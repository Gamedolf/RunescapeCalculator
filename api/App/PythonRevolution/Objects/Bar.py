import numpy as np


class AbilityBar():
    """
    The AbilityBar class containing all the properties the Ability Bar has in RuneScape.
    """

    def __init__(self, userInput):
        self.GCDStatus = False                  # When True, the ability bar is on a global cooldown
        self.GCDTime = 0                        # Time before the global cooldown wears of
        self.GCDMax = 3                         # Maximum time of a global cooldown
        self.FireStatus = False                 # When True, a chosen ability is allowed to be used
        self.FireN = None                       # The index of the ability to be fired in the current tick
        self.Rotation = []                      # Contains the abilities put on the bar
        self.N = 0                              # Amount of abilities on the bar
        self.AbilNames = []                     # A list of names of abilities on the bar
        self.AbilEquipment = []                 # A list of equipment allowed for using the abilities
        self.AbilStyles = []                    # A list of ability styles
        self.Threshold = 15                     # Adrenaline used for a threshold ability
        self.Style = ''

        self.Basic = 9 if userInput['FotS'] else 8                          # Adrenaline generated by a basic ability
        self.MaxAdrenaline = 110 if userInput['HeightenedSenses'] else 100  # Maximum amount of adrenaline

        # Check user input for a possible value for simulation time and starting adrenaline
        if userInput['simulationTime'] != '' and userInput['Adrenaline'] != '' and \
                1 <= userInput['simulationTime'] <= 3600 and 0 <= userInput['Adrenaline'] <= 100:
            self.Adrenaline = round(userInput['Adrenaline'], 0)
        else:
            self.Adrenaline = 100                                       # Set starting adrenaline

        if userInput['Impatient'] > 0:                                  # Basic Ability Adrenaline gain change due to Impatient perk
            self.Basic += 3 * 0.09 * userInput['Impatient']

        if not userInput['Ring'] == 'RoV' and not userInput['CoE']:     # Ultimate adrenaline cost
            self.Ultimate = 100
        elif userInput['Ring'] == 'RoV' and userInput['CoE']:
            self.Ultimate = 80
        else:
            self.Ultimate = 90

        # Groups of abilities which share a cooldown
        self.SharedCDs = [
            ['Surge', 'Escape'],
            ['Forceful Backhand', 'Stomp', 'Tight Bindings', 'Rout', 'Deep Impact', 'Horror'],
            ['Backhand', 'Kick', 'Binding Shot', 'Demoralise', 'Impact', 'Shock'],
            ['Fragmentation Shot', 'Combust'],
            ['Metamorphosis', 'Sunshine']
        ]

        if not userInput['DualLeng']:
            self.SharedCDs.append(['Destroy', 'Hurricane'])

        # Groups of abilities which cannot appear together on the ability bar
        self.Invalid = [
            ['Lesser Smash', 'Smash'],
            ['Lesser Havoc', 'Havoc'],
            ['Lesser Sever', 'Sever'],
            ['Lesser Dismember', 'Dismember'],
            ['Fury', 'Greater Fury'],
            ['Barge', 'Greater Barge'],
            ['Flurry', 'Greater Flurry'],
            ['Lesser Combust', 'Combust'],
            ['Lesser Dragon Breath', 'Dragon Breath'],
            ['Lesser Sonic Wave', 'Sonic Wave'],
            ['Lesser Concentrated Blast', 'Concentrated Blast', 'Greater Concentrated Blast'],
            ['Lesser Snipe', 'Snipe'],
            ['Lesser Fragmentation Shot', 'Fragmentation Shot'],
            ['Lesser Needle Strike', 'Needle Strike'],
            ['Lesser Dazing Shot', 'Dazing Shot', 'Greater Dazing Shot'],
            ['Ricochet', 'Greater Ricochet'],
            ['Chain', 'Greater Chain'],
        ]

    def TimerCheck(self, logger):
        """
        Checks the global cooldown status.

        :param logger: The Logger object
        """

        if self.GCDStatus:
            self.GCDTime -= 1

            if self.GCDTime == 0:
                self.GCDStatus = False

                if logger.DebugMode:
                    logger.write(18)

        # For all abilities currently on cooldown
        for ability in self.Rotation:

            if ability.cdTime:
                ability.cdTime -= 1

                if not ability.cdTime:
                    if logger.DebugMode:
                        logger.write(22, ability.Name)

    def FireNextAbility(self, player, logger):
        """
        Checks if an ability is allowed to fire.

        :param player: The Player object
        :param logger: The Logger object
        """

        # Check for available ability
        for i in range(0, self.N):
            Ability = self.Rotation[i]

            if not Ability.cdTime:
                self.FireStatus = True
                adrenaline = 0

                if Ability.Type == 'Basic':
                    adrenaline += self.Basic
                    if Ability.Name == 'Dragon Breath' and player.DragonBreathGain:
                        adrenaline += 2

                elif Ability.Type == 'Threshold' and self.Adrenaline >= 50:
                    adrenaline = -self.Threshold

                elif Ability.Type == 'Ultimate':
                    if self.Adrenaline >= 60 and 'Igneous' in player.Cape and Ability.Name in {'Overpower', 'Deadshot', 'Omnipower'}:
                        adrenaline -= 60

                    elif self.Adrenaline >= 100:
                        if player.PerkUltimatums and Ability.Name in {'Overpower', 'Frenzy', 'Unload', 'Omnipower'} and 100 - self.Ultimate < player.Ur * 5:
                            adrenaline -= (100 - player.Ur * 5)
                        else:
                            adrenaline -= self.Ultimate

                else:
                    self.FireStatus = False

                if self.FireStatus:
                    self.FireN = i  # Index of ability is equal to for loop i

                    self.Adrenaline += adrenaline

                    if self.Adrenaline > self.MaxAdrenaline:
                        self.Adrenaline = self.MaxAdrenaline

                    if logger.DebugMode:
                        logger.write(36, self.Rotation[i].Name)

                    break  # Break because firing more than 1 ability wouldn't make sense

                else:
                    if logger.DebugMode:
                        logger.write(37, self.Rotation[i].Name)

    def SharedCooldowns(self, FireAbility, player, logger):
        """
        Check if abilities which share a cooldown have to go on cooldown or not.

        :param FireAbility: The ability activated in the current attack cycle.
        :param player: The player object.
        :param logger: The Logger object.
        """

        for group in self.SharedCDs:
            if FireAbility.Name in group:
                for Ability in group:
                    if Ability == FireAbility.Name:
                        pass
                    elif Ability in self.AbilNames:
                        idx = self.AbilNames.index(Ability)
                        self.Rotation[idx].cdTime = self.Rotation[idx].cdMax
                        player.Cooldown.append(self.Rotation[idx])

                        if logger.DebugMode:
                            logger.write(42, self.Rotation[idx].Name)

                # The ability will never occur in 2 groups (would not make sense)
                break
