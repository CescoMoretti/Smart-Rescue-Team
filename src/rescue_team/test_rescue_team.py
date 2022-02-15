from rescue_team_obj import Rescue_team_obj
import random


def main():
    broker = 'localhost'
    port = 1883
    client_id = f'team-{random.randint(0, 1000)}'
    

    team1 = Rescue_team_obj(broker, port, client_id)
    team1.start()

if __name__ == "__main__":
    main()