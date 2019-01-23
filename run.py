from devapp.app import app
from devapp.server import server

if __name__ == '__main__':
    import requests_cache
    from dotenv import load_dotenv

    load_dotenv()
    requests_cache.install_cache()
    app.run_server(debug=True)
