from src.data import check_registration
from src.menu import index_menu, new_pwd


def main():
    check_registration()

    while True:
        choice = index_menu()

        if choice == -1:
            break
        elif choice == 1:
            new_pwd()


if __name__ == "__main__":
    main()
