"""
This program controls the admin commands in the game.
Also any menu navigations.


Note: SpecimenImplant has a player's ID called "Sample #: 34225234"
Can have user input their sample #


"""

from time import sleep
# from pywinauto import keyboard, mouse
from arkdriver.driver.application import Application
from pathlib import Path
import json


class Driver:
    def __init__(self, application=None):
        if application is None:
            application = Application()
            application.start()
        self.app = application
        self.pane = application.pane

    def open_players_list(self):
        """ In spectator mode, lists all current players """
        self.app.set_focus()
        sleep(1)
        self.app.send_key_ctrl_n()

    def close_players_list(self):
        """ Closes the players list window """
        coords = self.app.locate_button_by_image('player_list', 'close_template')
        self.app.click(coords=coords)

    def save_players_list(self):
        """ Stores the list of all players """
        # TODO: Machine learning and OCR to get the text list
        pass

    def close_admin_menu(self):
        """ Closes the admin menu window """
        coords = self.app.locate_button_by_image('admin_menu', 'close_template')
        self.app.click(coords=coords)

    def resume_pause_menu(self):
        """ Closes the pause menu window """
        coords = self.app.locate_button_by_image('pause_menu', 'close_template')
        self.app.click(coords=coords)

    def close_pause_menu(self):
        """ Closes the pause menu window """
        coords = self.app.locate_button_by_image('pause_menu', 'resume_template')
        self.app.click(coords=coords)

    def exit_to_main_menu(self):
        """ Exits to the main menu """
        coords = self.app.locate_button_by_image('pause_menu', 'exit_to_main_menu_template')
        self.app.click(coords=coords)

    def target_player_name(self, name):
        """ While in spectator mode, find player and lock onto them """
        # TODO: Machine learning and OCR
        # TODO: Dynamically recognize a list and click to them
        pass

    def scrape_player_data(self):
        """ Gather player blueprint_data (e.g. player_id and tribe_id) """
        # TODO: machine learning to scrape images text and OCR
        pass

    def teleport_default(self):
        """ Teleport to a hidden location """
        # TODO: find a hidden place with x, y, z coodinates
        pass

    def copy_coords(self):
        """ Copies your current coordinates and rotation to clipboard in the form x,y,z Yaw pitch """
        self.write_console("ccc")

    def save_current_coordinates(self, map, name):
        """ Stores the coordinates into file with a name
        :param name: str, name for the coordinates
        """
        data = {"center": {}, "gen1": {}, "gen2": {}, "island": {},
                "scortched": {}, "ragnarok": {}, "extinction": {}, "aberration": {}}
        if map not in data:
            raise NotImplementedError("'{}' isn't part of the map list: {}".format(map, data.keys()))
        self.copy_coords()
        coords = [float(val) for val in self.app.get_from_clipboard().split()]
        file_path = Path.cwd() / Path('../logs/saved_coordinates.json')
        if file_path.exists():
            with open(file_path, 'r') as r:
                data = json.load(r)

        cc = {"x": coords[0], "y": coords[1], "z": coords[2], "yaw": coords[3], "pitch": coords[4]}
        data[map][name] = cc
        with open(file_path, "w") as w:
            json.dump(data, w)

    def write_console(self, *commands):
        self.app.set_focus()
        sleep(1)
        self.app.set_focus()
        self.app.save_to_clipboard_text("|".join(["{}".format(command) for command in commands]) + '|')
        self.app.send_key_tab()
        sleep(0.2)
        self.app.send_key_paste()
        sleep(1)
        self.app.send_key_enter()

    def write_console_args(self, args: list, *command_formats):
        """ player_ids is a list of player ids
            command_formats are commands in format form: "cheat GiveItemTO {} Pickaxe 1 1"
                where there is a '{}' in the string
         """
        commands = []
        for str_format in command_formats:
            commands.append(str_format.format(*args))
        self.write_console(*commands)


def main():
    # TODO: Ensure I'm signed into x
    from application import Application

    app = Application()
    app.start()
    app.wait_exists()
    sleep(5)
    app.set_focus()
    ark_driver = Driver(app)
    ark_driver.click_start()
    sleep(3)
    ark_driver.click_join_ark()
    sleep(10)
    ark_driver.search("mark")
    sleep(2)
    ark_driver.click_refresh()
    sleep(10)
    ark_driver.click_first_search_result()
    ark_driver.click_join()
    input("Press ENTER to exit...")


if __name__ == "__main__":
    main()
