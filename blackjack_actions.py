import random
import itertools as it
import pandas as pd

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

class Deck:
    def __init__(self, number_of_decks = 6, minimum_number_of_cards = 20):
        cards_in_single_deck = list(it.product([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11], ['H', 'D', 'C', 'S'])) 
        cards_in_multiple_decks = list(it.chain.from_iterable(it.repeat(x, number_of_decks) for x in cards_in_single_deck))
        self.cards = [Card(x[0], x[1]) for x in cards_in_multiple_decks]
        self.minimum_number_of_cards = minimum_number_of_cards
        self.number_of_decks = number_of_decks

    def remove_card(self):
        card = random.sample(self.cards, 1)
        self.cards.remove(card[0])
        return card[0]

    def shuffle(self):
        cards_in_single_deck = list(it.product([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11], ['H', 'D', 'C', 'S'])) 
        cards_in_multiple_decks = list(it.chain.from_iterable(it.repeat(x, self.number_of_decks) for x in cards_in_single_deck))
        self.cards = [Card(x[0], x[1]) for x in cards_in_multiple_decks]
        self.number_of_cards = len(self.cards)
        return

class Dealer:
    def __init__(self, max_total_to_hit = 17):
        self.max_total_to_hit = max_total_to_hit
        self.hand = []
        self.face_up_card = None

    def deal_dealer_hand(self, deck):
        self.hand.append(deck.remove_card())
        self.face_up_card = self.hand[0]
        self.hand.append(deck.remove_card())
        return
    
    def deal_dealer_remaining_cards(self, deck):
        while count_hand_total(self.hand) < self.max_total_to_hit:
            self.hand.append(deck.remove_card())       
        return

    def clear_dealer_cards(self):
        self.hand = []
        return

class Player:
    def __init__(self, decision_matrix):
        self.decision_matrix = decision_matrix
        self.hand = []
        self.hand_split = []
    
    def deal_player_hand(self, deck):
        self.hand.append(deck.remove_card())
        self.hand.append(deck.remove_card())
        self.hand_total = count_hand_total(self.hand)

    def player_decision(self, cards, dealer, split_allowed):
        try:
            if cards[0].value == cards[1].value and split_allowed:
                return self.decision_matrix.loc['Split: ' + str(cards[0].value), str(dealer.face_up_card.value)]
            elif max(cards, key=lambda card: card.value).value == 11:
                return self.decision_matrix.loc['Soft: ' + str(count_hand_total(cards)), str(dealer.face_up_card.value)]
            elif count_hand_total(cards) < 21 and count_hand_total(cards) >= 4:
                return self.decision_matrix.loc[str(count_hand_total(cards)), str(dealer.face_up_card.value)]
        except ValueError:
            print('Oh no! something went wrong')

    def hit(self, deck, deal_to_split_hand):
        if not deal_to_split_hand:
            self.hand.append(deck.remove_card())
        else:
            self.hand_split.append(deck.remove_card())
        return

    def split(self, deck):
        self.hand_split.append(self.hand[1])
        self.hand[1] = deck.remove_card()
        self.hand_split.append(deck.remove_card())
        return
    
    def clear_player_cards(self):
        self.hand = []
        self.hand_split = []
        self.hand_total = 0
        self.hand_split_total = 0
        self.deal_to_split_hand = False

class Game:
    def __init__(self, decision_matrix, number_of_decks = 6, minimum_number_of_cards = 20, dealer_max_total_to_hit = 17):
        self.deck = Deck(number_of_decks, minimum_number_of_cards)
        self.dealer = Dealer(dealer_max_total_to_hit)
        self.player = Player(decision_matrix)
        self.result = 0
        self.count = 0
        self.player_has_doubled = False
        self.player_split_has_doubled = False
        self.player_has_split = False
        
    def one_round(self):
        self.dealer.deal_dealer_hand(self.deck)
        self.player.deal_player_hand(self.deck)

        decision = self.player_action(deal_to_split_hand=False, split_allowed=True)
        if decision == 'P':
            self.player.split(self.deck)
            self.player_has_split = True

        self.player_series_of_actions(deal_to_split_hand=False)
        if self.player_has_split:
            self.player_series_of_actions(deal_to_split_hand=True)

        self.dealer.deal_dealer_remaining_cards(self.deck)

        self.determine_winner(self.dealer.hand, self.player.hand, self.player_has_doubled)
        if len(self.player.hand_split) != 0:
            self.determine_winner(self.dealer.hand, self.player.hand_split, self.player_split_has_doubled)

        self.count += count_cards(self.player.hand)
        self.count += count_cards(self.player.hand_split)
        self.count += count_cards(self.dealer.hand)

        return
    
    def player_series_of_actions(self, deal_to_split_hand):
        decision = self.player_action(deal_to_split_hand=deal_to_split_hand, split_allowed=False)
        while decision in ['H', 'D']:
            if decision == 'D' and not deal_to_split_hand:
                self.player.hit(self.deck, deal_to_split_hand=deal_to_split_hand)
                self.player_has_doubled = True 
                break
            elif decision == 'D' and deal_to_split_hand:
                self.player.hit(self.deck, deal_to_split_hand=deal_to_split_hand)
                self.player_split_has_doubled = True
                break
            else:
                self.player.hit(self.deck, deal_to_split_hand=deal_to_split_hand)

            if count_hand_total(self.player.hand) > 21 and not deal_to_split_hand:
                break
            elif count_hand_total(self.player.hand_split) > 21 and deal_to_split_hand:
                break
            
            decision = self.player_action(deal_to_split_hand=deal_to_split_hand, split_allowed=False)
            if decision in ['H', 'D']:
                decision = 'H'
            else:
                decision = 'S'
            
        return

    def player_action(self, deal_to_split_hand, split_allowed):
        if not deal_to_split_hand:
            return self.player.player_decision(self.player.hand, self.dealer, split_allowed=split_allowed)
        else:
            return self.player.player_decision(self.player.hand_split, self.dealer, split_allowed=split_allowed)

    def determine_winner(self, dealer_cards, player_cards, player_doubled):
        if player_doubled:
            double_factor = 2
        else:
            double_factor = 1

        if count_hand_total(player_cards) == 21:
            self.result += 1.5 * double_factor
        elif count_hand_total(player_cards) > 21:
            self.result -= 1 * double_factor
        elif count_hand_total(dealer_cards) > 21:
            self.result += 1 * double_factor
        elif count_hand_total(dealer_cards) > count_hand_total(player_cards):
            self.result -= 1 * double_factor
        elif count_hand_total(dealer_cards) < count_hand_total(player_cards):
            self.result += 1 * double_factor
        return

    def restart_table(self):
        self.dealer.clear_dealer_cards()
        self.player.clear_player_cards()
        self.result = 0
        self.player_has_doubled = False
        self.player_split_has_doubled = False
        self.player_has_split = False

        if len(self.deck.cards) < self.deck.minimum_number_of_cards:
            self.deck.shuffle()
            self.count = 0
        return
    
def count_hand_total(cards):
    if sum(card.value for card in cards) > 21 and max(cards, key=lambda card: card.value).value == 11:
        next(card for card in cards if card.value == 11).value = 1
    return sum(card.value for card in cards)

def count_cards(cards):
    count = 0
    for card in cards:
        if card.value in [2, 3, 4, 5, 6]:
            count += 1
        elif card.value in [1, 10, 11]:
            count -= 1
    return count