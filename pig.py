import random
import argparse
import time
import msvcrt
from unittest import result


class Die:
    def roll(self):
        return random.randint(1, 6)

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def add_score(self, points):
        self.score += points

class HumanPlayer(Player):
    def get_choice(self, turn_total, deadline=None):
        if deadline is None:
            return input("Roll (r) or Hold (h)? ").lower()

        print("Roll (r) or Hold (h)? ", end="", flush=True)

        while time.monotonic() < deadline:
            if msvcrt.kbhit():
                key = msvcrt.getwch().lower()

                if key in ("r", "h"):
                    print(key)
                    return key

            time.sleep(0.05)

        print("\nTime limit reached!")
        return None

class ComputerPlayer(Player):
    def get_choice(self, turn_total, deadline=None):
        hold_threshold = min(25, 100 - self.score)

        if turn_total >= hold_threshold:
            return "h"
        else:
            return "r"

class PlayerFactory:
    @staticmethod
    def create_player(player_type, name):
        if player_type == "human":
            return HumanPlayer(name)
        elif player_type == "computer":
            return ComputerPlayer(name)
        else:
            raise ValueError("Invalid player type")

class PigGame:
    def __init__(self, player1_type="human", player2_type="human"):
        self.players = [
            PlayerFactory.create_player(player1_type, "Player 1"),
            PlayerFactory.create_player(player2_type, "Player 2")
        ]
        self.die = Die()
        self.current_player = 0
        self.turn_total = 0

    def switch_player(self):
        self.current_player = (self.current_player + 1) % 2
        self.turn_total = 0

    def roll_die(self):
        roll = self.die.roll()
        print("You rolled:", roll)

        if roll == 1:
            print("You rolled a 1! Turn over.")
            print("You lost", self.turn_total, "turn points.")
            self.switch_player()
        else:
            self.turn_total += roll
            print("Turn total:", self.turn_total)

    def hold(self):
        player = self.players[self.current_player]
        player.add_score(self.turn_total)

        print(player.name, "holds.")
        print("Total score:", player.score)

        if player.score < 100:
            self.switch_player()

    def play(self, time_check=None, deadline=None):
        print("Welcome to the Game of Pig!")

        while True:
            if time_check is not None and time_check():
                return "timeout"
        
            player = self.players[self.current_player]
           
            print("\n", player.name, "'s turn")
            print("Total score:", player.score)
            print("Turn total:", self.turn_total)

            choice = player.get_choice(self.turn_total, deadline)

            if time_check is not None and time_check():
                return "timeout"

            if choice == "r":
                self.roll_die()
            elif choice == "h":
                self.hold()
            else:
                print("Invalid choice. Please enter 'r' or 'h'.")

            for player in self.players:
                if player.score >= 100:
                    print("\n", player.name, "wins!")
                    return

class TimedGameProxy:
    def __init__(self, game, time_limit=60):
        self.game = game
        self.time_limit = time_limit
        self.start_time = None

    def time_expired(self):
        return time.monotonic() - self.start_time >= self.time_limit

    def determine_winner(self):
        player1, player2 = self.game.players

        if player1.score > player2.score:
            print(player1.name, "wins with", player1.score, "points!")
        elif player2.score > player1.score:
            print(player2.name, "wins with", player2.score, "points!")
        else:
            print("The game is a tie!")

    def play(self):
        self.start_time = time.monotonic()
        deadline = self.start_time + self.time_limit

        result = self.game.play(
            time_check=self.time_expired,
            deadline=deadline
    )

        if result == "timeout":
            print("\nTime is up!")
            self.determine_winner()
    
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="The Game of Pig"
    )

    parser.add_argument(
        "--player1",
        choices=["human", "computer"],
        default="human"
    )

    parser.add_argument(
        "--player2",
        choices=["human", "computer"],
        default="human"
    )

    parser.add_argument(
        "--timed",
        action="store_true",
        help="Play a timed game with a 60-second limit"
)

args = parser.parse_args()

game = PigGame(args.player1, args.player2)

if args.timed:
    game = TimedGameProxy(game)

game.play()
    
