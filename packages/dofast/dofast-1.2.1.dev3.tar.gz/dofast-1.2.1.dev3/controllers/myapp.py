from dofast.flask.router import get_blueprint

bp = get_blueprint(__name__)

@bp.route('/', methods=["POST", "GET"])
def hello():
    return "hello"
