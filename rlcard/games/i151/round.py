'''
    File name: bridge/round.py
    Author: William Hale
    Date created: 11/25/2021
'''

from rlcard.games.i151.dealer import I151Dealer

from rlcard.games.i151.utils.action_event import *
from rlcard.games.i151.utils.move import *


class I151Round:

    @property
    def round_phase(self):
        if self.is_over():
            result = 'game over'
        else:
            result = 'play card'
        return result

    @property
    def active_player_count(self):
        count = 0
        for p in self.players:
            if not self.is_out(p):
                count += 1
        return count

    def __init__(self, num_players: int, board_id: int, np_random, point_limit: int = 1, successive_reward: int = -10):
        ''' Initialize the round class

            The round class maintains the following instances:
                1) dealer: the dealer of the round; dealer has trick_pile
                2) players: the players in the round; each player has his own hand_pile
                3) current_player_id: the id of the current player who has the move
                4) doubling_cube: 2 if contract is doubled; 4 if contract is redoubled; else 1
                5) play_card_count: count of PlayCardMoves
                5) move_sheet: history of the moves of the players (including the deal_hand_move)

            The round class maintains a list of moves made by the players in self.move_sheet.
            move_sheet is similar to a chess score sheet.
            I didn't want to call it a score_sheet since it is not keeping score.
            I could have called move_sheet just moves, but that might conflict with the name moves used elsewhere.
            I settled on the longer name "move_sheet" to indicate that it is the official list of moves being made.

        Args:
            num_players: int
            board_id: int
            np_random
        '''
        self.dealer_id = board_id
        self.np_random = np_random
        self.dealer: I151Dealer = I151Dealer(self.np_random)
        self.players: List[I151Player] = []
        self.num_players = num_players
        for player_id in range(num_players):
            self.players.append(I151Player(player_id=player_id, np_random=self.np_random))
        self.current_player_id: int = self.dealer_id
        self.take_two: bool = False
        self.took: bool = False
        self.asked: int = -1
        self.point_limit = point_limit
        self.successive_reward = successive_reward
        self.game_over = False
        self.counter = 0
        self.move_sheet: List[I151Move] = []
        self.move_sheet.append(
            DealHandMove(dealer=self.players[self.dealer_id], shuffled_deck=self.dealer.shuffled_deck))

    def is_over(self) -> bool:
        ''' Return whether the current game is over
        '''
        is_over = len(self.players[self.current_player_id].hand) == 0
        return is_over or self.counter > 512

    def get_current_player(self) -> I151Player or None:
        current_player_id = self.current_player_id
        return None if current_player_id is None else self.players[current_player_id]

    def take(self, nb_cards: int = 1):
        current_player = self.get_current_player()
        if current_player is None:
            return
        self.dealer.take(current_player, nb_cards)

    def is_out(self, player: I151Player):
        return player.point >= self.point_limit

    def set_point(self, player: I151Player):
        weight = np.sum([WEIGHTS[c.card_id] for c in player.hand])
        if len(player.points) >= 2 and np.sum([abs(p) for p in player.points[-2:]]) == 0 and weight == 0:
            weight = self.successive_reward
        player.points.append(weight)

    def next_player(self):
        active_count = self.active_player_count
        if active_count <= 1:
            return
        self.current_player_id = (self.current_player_id + 1) % active_count
        while self.is_out(self.players[self.current_player_id]):
            self.current_player_id = (self.current_player_id + 1) % active_count

    def end_game(self):
        if self.game_over:
            return
        for player in self.players:
            self.set_point(player)
        self.game_over = True
        self.counter = 0

    def make_call(self, action: CallActionEvent):
        self.counter += 1
        # when current_player takes CallActionEvent step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        if isinstance(action, PassAction):
            self.took = False
            self.take_two = False
            self.next_player()
            self.move_sheet.append(MakePassMove(current_player))
            return
        elif isinstance(action, DrawAction) or isinstance(action, DoubleDrawAction):
            if not self.took:
                nb_cards = 1
                self.took = True
                if self.take_two:
                    nb_cards = 2
                self.take(nb_cards)
                if self.take_two or not self.dealer.table:
                    self.next_player()
                    self.took = False
                    self.take_two = False
                make_move = MakeDrawMove(current_player) if isinstance(action, DrawAction) else MakeDoubleDrawMove(
                    current_player)
                self.move_sheet.append(make_move)
            return
        elif isinstance(action, AskAction): # Do not return
            # cards = action.action.cards
            self.asked = action.ask
            # self.dealer.played(current_player, cards)
            self.move_sheet.append(MakeAskMove(current_player, ask_action=action))
        if not self.is_over():
            self.next_player()
        else:
            self.end_game()

    def play_card(self, action: PlayCardAction):
        self.counter += 1
        # when current_player takes PlayCardAction step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(PlayCardMove(current_player, action))
        cards = action.cards
        self.dealer.played(current_player, cards)
        top_card: I151Card = self.dealer.top_card
        self.take_two = top_card.is_as
        self.asked = -1
        self.took = False
        if len(current_player.hand) == 0:
            if self.active_player_count > 2 or not top_card.is_queen:
                self.end_game()
            else:
                can_take = len(self.dealer.table) > 3
                if not can_take:
                    for c in self.dealer.table:
                        if not c.is_queen:
                            can_take = True
                            break
                if can_take:
                    self.take(1)
                    self.took = True
                else:
                    self.end_game()
        else:
            if top_card.is_queen:
                self.next_player()
            if not top_card.is_eight: # Do not pass if the top card is eight.
                self.next_player()

    def get_perfect_information(self):
        state = {}
        state['move_count'] = len(self.move_sheet)
        state['current_player_id'] = self.current_player_id
        state['round_phase'] = self.round_phase
        state['took'] = self.took
        state['take_two'] = self.take_two
        state['hands'] = [player.hand for player in self.players]
        return state

    def print_scene(self):
        print(
            f'===== Board: {self.dealer_id} move: {len(self.move_sheet)} player: {self.players[self.current_player_id]} phase: {self.round_phase} =====')
        print(f'dealer={self.players[self.dealer_id]}')

        for player in self.players:
            print(f'{player}: {[str(card) for card in player.hand]}')
