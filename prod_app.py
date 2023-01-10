from api import create_app

app = create_app(is_production=True)

if __name__ == "__main__":
    app.run()
