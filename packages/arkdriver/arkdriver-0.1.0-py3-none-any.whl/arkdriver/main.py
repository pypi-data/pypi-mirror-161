from arkdriver.server import GameBotServer
from arkdriver.lib import Ini
from pathlib import Path

__testing__ = False


def run():
    file_path = Path(__file__).parent / Path('config.ini')
    config = Ini(file_path)
    host = config['NETWORK']['ip_address']
    port = int(config['NETWORK']['port'])

    if not __testing__:
        server = GameBotServer(host=host, port=port)
        server.run()


if __name__ == "__main__":
    run()
