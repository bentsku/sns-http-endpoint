from app import create_app
from app.config_app import Config

app = create_app(Config)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000)
