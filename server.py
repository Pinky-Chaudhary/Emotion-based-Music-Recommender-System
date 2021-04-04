from views import app
from model import connect_to_db
if __name__ == '__main__':
    connect_to_db(app)
    app.run()
