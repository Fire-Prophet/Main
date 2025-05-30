from mini_games.rock_paper_scissors import RockPaperScissorsGame
from mini_games.dice_odd_even import DiceOddEven
from mini_games.timing_game import TimingGame
from mini_games.direction_key_game import DirectionKeyGame
from PyQt6.QtCore import QTimer
import random

class CombatManager:
    def __init__(self, player, monster, game_window, item_manager):
        self.player = player
        self.monster = monster
        self.game_window = game_window
        self.item_manager = item_manager
        self.in_combat = True

        self.start_battle()

    def start_battle(self):
        self.game_window.update_description(
            f"⚔️ {self.monster.name}가 나타났다!\n전투를 시작합니다!"
        )
        self.game_window.update_status()
        self.perform_turn()

    def perform_turn(self):
        if not self.in_combat:
            return

        # 미니게임 클래스를 랜덤으로 선택하고 인스턴스 생성
        mini_game_class = self.select_random_mini_game()
        self.current_mini_game = mini_game_class(finish_callback=self.process_mini_game_result)

        # 새 창으로 미니게임 띄우기
        self.current_mini_game.show()

    def select_random_mini_game(self):
        games = [
            RockPaperScissorsGame,
            DiceOddEven,
            TimingGame,
            DirectionKeyGame
        ]
        return random.choice(games)

    def process_mini_game_result(self, success):
        if not self.in_combat:
            return

        # 미니게임 창 닫기
        self.current_mini_game.close()

        if success:
            damage = 20
            self.monster.take_damage(damage)
            self.game_window.update_description(
                f"🎯 미니게임 성공! {self.monster.name}에게 {damage}의 피해!"
            )

            if self.monster.defeated:
                self.end_combat(victory=True)
                return
        else:
            damage = self.monster.attack_power
            self.player.take_damage(damage)
            self.game_window.update_description(
                f"💥 미니게임 실패! {self.monster.name}에게 {damage}의 피해를 입었습니다!"
            )

            if self.player.hp <= 0:
                self.end_combat(victory=False)
                return

        self.game_window.update_status()

        # 턴 딜레이 후 다음 턴
        QTimer.singleShot(1000, self.perform_turn)

    def end_combat(self, victory):
        if not self.in_combat:
            return

        self.in_combat = False
        self.game_window.current_monster = None

        if victory:
            dropped_item = self.item_manager.get_random_item()
            self.player.add_item(dropped_item)

            self.monster.defeated = True
            self.game_window.update_description(
                f"🎉 {self.monster.name} 처치 성공!\n📦 아이템 획득: {dropped_item.name}"
            )
        else:
            self.game_window.update_description("💀 전투에서 패배했습니다...")

        self.game_window.update_status()
        self.game_window.update_choices()
