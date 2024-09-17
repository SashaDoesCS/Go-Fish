import random
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


# Card Class
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def get_rank_value(self):
        rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                      'K': 13, 'A': 14}
        return rank_order[self.rank]

    def get_suit_symbol(self):
        suit_symbols = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}
        return suit_symbols[self.suit]


# Deck Class
class Deck:
    def __init__(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        if not self.is_empty():
            return self.cards.pop()

    def is_empty(self):
        return len(self.cards) == 0


# Insertion Sort for Player's Hand
def insertion_sort_hand(hand):
    for i in range(1, len(hand)):
        key_card = hand[i]
        j = i - 1
        while j >= 0 and hand[j].get_rank_value() > key_card.get_rank_value():
            hand[j + 1] = hand[j]
            j -= 1
        hand[j + 1] = key_card


# Player Class
class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.hand = []
        self.books = []
        self.is_human = is_human

    def ask_for_card(self, rank, opponent):
        requested_cards = [card for card in opponent.hand if card.rank == rank]
        if requested_cards:
            for card in requested_cards:
                opponent.hand.remove(card)
            return requested_cards
        return []

    def add_to_hand(self, cards):
        self.hand.extend(cards)
        insertion_sort_hand(self.hand)  # Sort the hand whenever a card is added

    def remove_from_hand(self, rank):
        matching_cards = [card for card in self.hand if card.rank == rank]
        self.hand = [card for card in self.hand if card.rank != rank]
        return matching_cards

    def check_for_books(self):
        ranks_in_hand = [card.rank for card in self.hand]
        for rank in set(ranks_in_hand):
            if ranks_in_hand.count(rank) == 4:
                self.books.append(rank)
                self.remove_from_hand(rank)

    def has_cards(self):
        return len(self.hand) > 0


# GoFishGame Class
class GoFishGame:
    def __init__(self, player_names, is_human_flags):
        self.deck = Deck()
        self.players = [Player(name, is_human) for name, is_human in zip(player_names, is_human_flags)]
        self.current_player_index = 0
        self.deal_cards()

    def deal_cards(self):
        for player in self.players:
            for _ in range(5):  # Deal 5 cards to each player
                player.add_to_hand([self.deck.deal()])

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def check_winner(self):
        return max(self.players, key=lambda player: len(player.books))

    def is_game_over(self):
        return self.deck.is_empty() or all(not player.has_cards() for player in self.players)


# GUI Class
class GoFishGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Go Fish Game")

        # Create the game with one human player and two computer players
        self.game = GoFishGame(["You", "Computer 1", "Computer 2"], [True, False, False])

        # Labels to show player hands and books
        self.player_hand_frame = tk.Frame(self.root)
        self.player_hand_frame.grid(row=0, column=0, padx=10, pady=10)

        self.player_books_label = tk.Label(self.root, text="Your Books:")
        self.player_books_label.grid(row=0, column=1)

        # Buttons to request cards and manage turns
        self.ask_button = tk.Button(self.root, text="Ask for Card", command=self.ask_for_card)
        self.ask_button.grid(row=2, column=0)

        self.next_turn_button = tk.Button(self.root, text="Next Turn", command=self.next_turn)
        self.next_turn_button.grid(row=2, column=1)

        # Update initial state of the game board
        self.update_board()

    def ask_for_card(self):
        current_player = self.game.get_current_player()
        if current_player.is_human:
            opponent = self.game.players[(self.game.current_player_index + 1) % len(self.game.players)]
            rank = simpledialog.askstring("Ask for Card", f"{current_player.name}, ask for a card rank:")

            if rank:
                requested_cards = current_player.ask_for_card(rank, opponent)
                if requested_cards:
                    messagebox.showinfo("Card Request", f"{opponent.name} had {len(requested_cards)} {rank}(s).")
                    current_player.add_to_hand(requested_cards)
                    current_player.check_for_books()
                else:
                    messagebox.showinfo("Go Fish", "Go Fish! Drawing a card from the deck.")
                    current_player.add_to_hand([self.game.deck.deal()])
                self.update_board()
        else:
            self.computer_turn()

    def computer_turn(self):
        current_player = self.game.get_current_player()
        opponent = random.choice([p for p in self.game.players if p != current_player])
        rank = random.choice([card.rank for card in current_player.hand])
        requested_cards = current_player.ask_for_card(rank, opponent)
        if requested_cards:
            messagebox.showinfo("Card Request",
                                f"{current_player.name} asked {opponent.name} for {rank}(s) and received {len(requested_cards)} card(s).")
            current_player.add_to_hand(requested_cards)
            current_player.check_for_books()
        else:
            messagebox.showinfo("Go Fish", f"{current_player.name} went fishing!")
            current_player.add_to_hand([self.game.deck.deal()])
        self.update_board()

    def next_turn(self):
        if self.game.is_game_over():
            winner = self.game.check_winner()
            messagebox.showinfo("Game Over", f"Game Over! {winner.name} wins with {len(winner.books)} books!")
            self.root.quit()
        else:
            self.game.next_turn()
            current_player = self.game.get_current_player()
            if not current_player.is_human:
                self.computer_turn()
            self.update_board()

    def update_board(self):
        current_player = self.game.get_current_player()

        # Clear current player hand frame
        for widget in self.player_hand_frame.winfo_children():
            widget.destroy()

        if current_player.is_human:
            for i, card in enumerate(current_player.hand):
                card_label = tk.Label(self.player_hand_frame, text=f"{card.rank}{card.get_suit_symbol()}",
                                      borderwidth=2, relief="solid", padx=5, pady=5)
                card_label.grid(row=0, column=i, padx=5)
        books_text = ", ".join(current_player.books)
        self.player_books_label.config(text=f"Your Books: {books_text}")


# Main Program to Start the Game
if __name__ == "__main__":
    root = tk.Tk()
    app = GoFishGUI(root)
    root.mainloop()
