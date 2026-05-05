from app import create_app
from app.extensions import db
from app.seed import seed_data

app = create_app()


@app.cli.command('init-db')
def init_db_command():
    # Create all tables and insert starter data for first-time setup.
    db.create_all()
    seed_data()
    print('Database initialized successfully.')


if __name__ == '__main__':
    app.run(host='dpg-d7geethf9bms73at7in0-a', port=5432, debug=True)
