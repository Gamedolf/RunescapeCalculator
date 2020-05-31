import numpy as np
import LoopObjects
import DummyObject
import BarObject
import AbilityObject
import PlayerObject
import CombatChecks as CC


# Checks for a cycle in the current revolution bar
def CycleCheck(bar, player, dummy, Do, loop):
    loop.nAC += 1  # Number of times the loop has initiated an attack cycle

    # Array containing all names of the abilities currently on cooldown
    cdNames = [ability.Name for ability in player.Cooldown]

    for i in range(0, bar.N):  # For every ability on the bar

        # Construct the cooldown array for the current attack cycle
        if bar.Rotation[i].Name in cdNames:  # If ability i is on cooldown
            loop.cdTimes[i] = player.Cooldown[cdNames.index(bar.Rotation[i].Name)].cdTime
        else:
            loop.cdTimes[i] = 0

    # Array consisting of array of cd times, loop time, adrenaline and puncture stack
    loop.ConditionList.append([loop.cdTimes[0: bar.N].copy(), bar.Adrenaline, dummy.nPuncture, player.AbilCritBuff, loop.n * .6])

    # For every Array in ConditionList created at an previous attack cycle
    for i in range(0, loop.nAC - 1):
        # CONDITION 1: If the adrenaline is equal
        if loop.ConditionList[i][1] == loop.ConditionList[-1][1]:
            # CONDITION 2: If the cooldown array is equal
            if (loop.ConditionList[i][0] == loop.ConditionList[-1][0]).all():
                # CONDITION 3: If the puncture stack is equal
                if loop.ConditionList[i][2] == loop.ConditionList[-1][2]:
                    # CONDITION 3: If the critical hit boost is equal
                    if loop.ConditionList[i][3] == loop.ConditionList[-1][3]:

                        loop.CycleFound = True  # A cycle has been found!

                        loop.CycleTime = loop.ConditionList[-1][4] - loop.ConditionList[i][4]  # The cycle time

                        loop.Cycle1More = loop.CycleTime    # Set the time for the next cycle
                        loop.CycleStart = loop.n * .6       # Starting time of the next cycle

                        loop.CycleConvergenceTime = loop.CycleStart - loop.CycleTime  # Convergence time

                        if Do.HTMLwrite:
                            Do.Text += f'<li style="color: {Do.cycle_color};">CYCLE FOUND, EXTENDING RUN BY 1x CYCLETIME: {round(loop.CycleTime, 1)}s</li>\n'

    return None


def CycleRotation(bar, player, dummy, Do, loop):
    loop.Cycle1More -= .6  # Subtract tick time

    # If Cycle1More reached 0 then cycle is no more
    if loop.Cycle1More < 0.01:

        # !!! important for accurate results, check 1 more time for possible bleeds/punctures
        CC.TimerStatuses(bar, player, dummy, Do, loop)

        # Check for redundant abilities (abilities which do not occur in the rotation)
        for j in range(0, bar.N):

            # If an ability has not been fired during the cycle verification
            if not loop.nFA[j]:
                loop.Redundant.extend([bar.Rotation[j].Name])

        # End the while loop prematurely
        loop.runLoop = False

        if Do.HTMLwrite:
            Do.Text += f'<li style="color: {Do.cycle_color};">VERIFICATION LOOP COMPLETED: RETURN RESULTS</li>'
