from goblet.deploy import Deployer
from goblet import Goblet
from goblet.test_utils import get_responses


class TestDeployer:

    def test_deploy_http_function(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_PROJECT", "goblet")
        monkeypatch.setenv("GOOGLE_LOCATION", "us-central1")
        monkeypatch.setenv("GOBLET_TEST_NAME", "deployer-function-deploy")
        monkeypatch.setenv("GOBLET_HTTP_TEST", "REPLAY")

        app = Goblet(function_name="goblet_example", region='us-central-1')
        setattr(app, "entrypoint", 'app')

        # TODO: switch to http
        app.handlers['schedule'].register_job('test-job', None, kwargs={'schedule': '* * * * *', 'kwargs': {}})

        Deployer().deploy(app, only_function=True)

        responses = get_responses('deployer-function-deploy')
        assert(len(responses) == 4)

    def test_destroy_http_function(self, monkeypatch):
        monkeypatch.setenv("GOOGLE_PROJECT", "goblet")
        monkeypatch.setenv("GOOGLE_LOCATION", "us-central1")
        monkeypatch.setenv("GOBLET_TEST_NAME", "deployer-function-destroy")
        monkeypatch.setenv("GOBLET_HTTP_TEST", "REPLAY")

        app = Goblet(function_name="goblet_example", region='us-central-1')

        Deployer().destroy(app)

        responses = get_responses('deployer-function-destroy')
        assert(len(responses) == 1)
        assert(responses[0]['body']['metadata']['type'] == 'DELETE_FUNCTION')
        assert(responses[0]['body']['metadata']['target'] == "projects/goblet/locations/us-central1/functions/goblet_test_app")
