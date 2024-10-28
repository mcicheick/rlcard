'''
    File name: test_i151_game.py
    Author: William Hale
    Date created: 11/25/2021
'''

import unittest

import numpy as np

from rlcard.games.i151.dealer import I151Dealer
from rlcard.games.i151.game import I151Game as Game
from rlcard.games.i151.player import I151Player
from rlcard.games.i151.utils.i151_card import I151Card
from rlcard.games.i151.utils.move import DealHandMove
from rlcard.games.i151.utils.parameters import AVAILABLE_ACTIONS_LENGTH, CARD_LENGTH


class TestI151Game(unittest.TestCase):

    def test_get_num_players(self):
        game = Game(nb_players=2)
        num_players = game.get_num_players()
        self.assertEqual(num_players, 2)

    def test_get_num_actions(self):
        game = Game(nb_players=2)
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, AVAILABLE_ACTIONS_LENGTH)

    def test_i151_dealer(self):
        dealer = I151Dealer(np.random.RandomState())
        current_deck = I151Card.get_deck()
        deck_card_ids = [card.card_id for card in current_deck]
        self.assertEqual(deck_card_ids, list(range(CARD_LENGTH)))
        # Deal 13 cards.
        player = I151Player(player_id=0, np_random=np.random.RandomState())
        dealer.deal_cards(player=player, num=8)
        self.assertEqual(len(dealer.shuffled_deck), CARD_LENGTH)
        self.assertEqual(len(dealer.stock_pile), CARD_LENGTH - 8)
        self.assertEqual(len(current_deck), CARD_LENGTH)
        self.assertEqual(len(I151Card.get_deck()), CARD_LENGTH)
        # Pop top_card from current_deck.
        top_card = current_deck.pop(-1)
        self.assertEqual(str(top_card), "8S")
        self.assertEqual(len(current_deck), CARD_LENGTH - 1)
        self.assertEqual(len(I151Card.get_deck()), CARD_LENGTH)

    def test_init_game(self):
        player_ids = list(range(4))
        game = Game(nb_players=4, initial_hand_size=8)
        state, current_player = game.init_game()
        self.assertEqual(len(game.round.move_sheet), 1)
        self.assertIn(current_player, player_ids)
        self.assertEqual(len(game.actions), 0)
        self.assertEqual(len(game.round.players[current_player].hand), 8)  # current_player has 13 cards
        self.assertEqual(len(game.round.dealer.shuffled_deck), CARD_LENGTH)
        self.assertEqual(len(game.round.dealer.stock_pile), 0)
        self.assertEqual(state['player_id'], current_player)
        self.assertEqual(len(state['hand']), 8)

    def test_step(self):
        game = Game()
        _, current_player_id = game.init_game()
        legal_actions = game.judger.get_legal_actions()
        action = np.random.choice(legal_actions)
        print(
            f'test_step current_player_id={current_player_id} action={action} legal_actions={[str(action) for action in legal_actions]}')
        _, next_player_id = game.step(action)
        next_legal_actions = game.judger.get_legal_actions()
        print(
            f'test_step next_player_id={next_player_id} next_legal_actions={[str(action) for action in next_legal_actions]}')

    def test_play_game(self):
        game = Game()
        next_state, next_player_id = game.init_game()
        deal_hand_move = game.round.move_sheet[0]
        self.assertTrue(isinstance(deal_hand_move, DealHandMove))
        print(f'test_play_game {deal_hand_move}')
        while not game.is_over():
            current_player_id = game.round.current_player_id
            self.assertEqual(current_player_id, next_player_id)
            legal_actions = game.judger.get_legal_actions()
            action = np.random.choice(legal_actions)
            print(f'test_play_game {current_player_id} {action} from {[str(x) for x in legal_actions]}')
            next_state, next_player_id = game.step(action)
        player = game.round.players[game.round.current_player_id]
        hand = player.hand
        self.assertTrue(not hand)

    def test_print_scene(self):
        game = Game()
        next_state, next_player_id = game.init_game()
        deal_hand_move = game.round.move_sheet[0]
        self.assertTrue(isinstance(deal_hand_move, DealHandMove))
        while not game.is_over():
            current_player_id = game.round.current_player_id
            self.assertEqual(current_player_id, next_player_id)
            legal_actions = game.judger.get_legal_actions()
            action = np.random.choice(legal_actions)
            game.round.print_scene()
            next_state, next_player_id = game.step(action)
        game.round.print_scene()
        player = game.round.players[game.round.current_player_id]
        hand = player.hand
        self.assertTrue(not hand)


if __name__ == '__main__':
    unittest.main()
