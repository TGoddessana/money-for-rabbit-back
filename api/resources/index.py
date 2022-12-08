from flask import make_response, render_template
from flask_restful import Resource


class IndexPage(Resource):
    @classmethod
    def get(cls):
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("index.html"), 200, headers)
