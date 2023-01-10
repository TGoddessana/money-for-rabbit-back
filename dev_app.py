from api import create_app

app = create_app(is_production=False)

if __name__ == "__main__":
    app.run()
