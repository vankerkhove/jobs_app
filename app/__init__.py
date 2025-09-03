import os

from flask import Flask


def create_app():

    app = Flask(__name__, instance_relative_config=True)
    print(app.instance_path)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'jobs.sqlite'),
    )
    
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import jobs_db
    jobs_db.init_app(app)
    
    from . import jobs
    app.register_blueprint(jobs.bp)
    app.add_url_rule('/', endpoint='index')

    return app