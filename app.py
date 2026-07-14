import tkinter as tk

from config.database_config import APP_USER_ID, DB_CONFIG
from controllers.inventory_controller import InventoryController
from repositories.mysql_repository import MySQLInventoryRepository
from views.inventory_view import InventoryView


def main() -> None:
    root = tk.Tk()

    view = InventoryView(root)

    repository = MySQLInventoryRepository(
        db_config=DB_CONFIG,
        id_usuario=APP_USER_ID,
    )

    InventoryController(
        view=view,
        repository=repository,
    )

    root.mainloop()


if __name__ == "__main__":
    main()
