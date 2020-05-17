from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app
from models import db, setup_migrate

setup_migrate(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
