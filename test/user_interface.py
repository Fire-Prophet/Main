class UserInterface:
    def __init__(self, app_name="My Console App"):
        self.app_name = app_name
        self.menu_options = {
            "1": "데이터 로드",
            "2": "데이터 처리",
            "3": "결과 저장",
            "4": "종료"
        }
        self.registered_actions = {} # Maps option number to a callable function

    def register_action(self, option_number, action_function, description=""):
        """Registers a function to be called when a menu option is selected."""
        if option_number in self.menu_options:
            self.registered_actions[option_number] = action_function
            if description: # Allow overriding default description
                self.menu_options[option_number] = description
            print(f"Action registered for option {option_number}: {self.menu_options[option_number]}")
        else:
            print(f"Error: Option {option_number} is not a valid menu option.")

    def _display_menu(self):
        """Displays the main menu to the user."""
        print(f"\n--- {self.app_name} ---")
        for key, value in self.menu_options.items():
            print(f"{key}. {value}")
        print("-----------------------")

    def _get_user_choice(self):
        """Gets user input for menu selection."""
        while True:
            choice = input("선택하세요: ").strip()
            if choice in self.menu_options:
                return choice
            else:
                print("유효하지 않은 선택입니다. 다시 시도해주세요.")

    def run(self):
        """Runs the main loop of the user interface."""
        print(f"Welcome to {self.app_name}!")
        while True:
            self._display_menu()
            choice = self._get_user_choice()

            if choice == "4":
                print("애플리케이션을 종료합니다. 안녕히 계세요!")
                break
            elif choice in self.registered_actions:
                try:
                    self.registered_actions[choice]()
                except Exception as e:
                    print(f"오류 발생: {e}")
            else:
                print(f"'{self.menu_options[choice]}' 기능은 아직 구현되지 않았습니다.")

# Dummy functions to demonstrate functionality
def load_data_action():
    print("데이터를 로드하는 중...")
    # Simulate data loading
    import time
    time.sleep(1)
    print("데이터 로드 완료.")

def process_data_action():
    print("데이터를 처리하는 중...")
    # Simulate data processing
    import time
    time.sleep(2)
    print("데이터 처리 완료.")

def save_results_action():
    print("결과를 저장하는 중...")
    # Simulate saving results
    import time
    time.sleep(1.5)
    print("결과 저장 완료.")

if __name__ == "__main__":
    ui = UserInterface("데이터 관리 시스템")
    ui.register_action("1", load_data_action)
    ui.register_action("2", process_data_action)
    ui.register_action("3", save_results_action) # Registering an action for an existing option
    # ui.register_action("5", lambda: print("새로운 기능 실행"), "새로운 기능") # Example of adding a new option
    ui.run()
