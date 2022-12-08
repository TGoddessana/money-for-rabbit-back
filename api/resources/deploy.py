import os

import git
from flask_restful import Resource


class DeployServer(Resource):
    @classmethod
    def post(cls):
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        repo = git.Repo(BASE_DIR, search_parent_directories=True)
        origin = repo.remotes.origin
        origin.pull()
        return "", 204
