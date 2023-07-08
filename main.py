from dspace import DSpaceClient


def main():
    client = DSpaceClient("https://api7.dspace.org/server/")
    client.login("dspacedemo+admin@gmail.com", "dspace")
    print(client.get_items())


if __name__ == '__main__':
    main()
