import json
import os

from goblet.utils import get_g_dir, get_dir
from goblet.__version__ import __version__


def create_goblet_dir(name):
    """Creates a new goblet directory with a sample main.py, requirements.txt, and config.json"""
    try:
        os.mkdir(get_g_dir())
    except FileExistsError:
        pass
    with open(f"{get_g_dir()}/config.json", "w") as f:
        f.write(json.dumps({"cloudfunction": {}}, indent=4))
    with open("requirements.txt", "w") as f:
        f.write(f"goblet-gcp=={__version__}")
    with open("main.py", "w") as f:
        f.write(
            f"""from goblet import Goblet, jsonify

app = Goblet(function_name="goblet-{name}")

@app.http()
def main(request):
    return jsonify(request.json)

# route
# @app.route('/hello')
# def home():
#     return jsonify("goodbye")

# schedule
# @app.schedule('5 * * * *')
# def scheduled_job():
#     return jsonify("success")

# pubsub topic
# @app.topic('test_topic')
# def topic(data):
#     app.log.info(data)
#     return
"""
        )
    with open("README.md", "w") as f:
        f.write(
            f"""# goblet-{name}

autocreated by goblet

To test endpoints locally run `goblet local`
To deploy cloudfunctions and other gcp resources defined in `main.py` run `goblet deploy`

To check out goblet documentation go to [docs](https://anovis.github.io/goblet/docs/build/html/index.html)
"""
        )


def write_dockerfile():
    with open(f"{get_dir()}/Dockerfile", "w") as f:
        f.write(
            """# https://hub.docker.com/_/python
FROM python:3.7-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

# Install dependencies.
RUN pip install -r requirements.txt

# Run the web service on container startup.
CMD exec functions-framework --target=goblet_entrypoint
"""
        )
