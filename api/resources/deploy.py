from flask_restful import Resource
import os, git


class DeployServer(Resource):
    def post(self):
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        repo = git.Repo(BASE_DIR, search_parent_directories=True)
        origin = repo.remotes.origin
        origin.pull()
        return "Pythonanywhere 서버에 성공적으로 업로드되었습니다!", 200
