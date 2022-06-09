import ujson
import requests

from flask import request, Response
from app.api import bp
from app.api import redis_helper as rd
from app.api.errors import bad_request


def jsonify(resp: dict, status: int = 200):
    json_resp = Response(ujson.dumps(resp) + "\n", mimetype="application/json", status=status)
    return json_resp


@bp.route('/', methods=['GET'])
def healthcheck():
    return jsonify({"status": "running"})


@bp.route('/endpoint-<string:short_uid>', methods=['POST'])
def sns_endpoint(short_uid):
    if rd.is_deleted_endpoint(short_uid):
        return jsonify({"error": "deleted endpoint"}, status=500)

    print(request.headers)
    if "X-Amz-Sns-Message-Type" in request.headers:
        log = {
            "headers": dict(request.headers.items()),
            "body": request.get_json(force=True)
        }
        rd.add_logs_to_endpoint(token=short_uid, log_data=ujson.dumps(log))
        if request.headers["X-Amz-Sns-Message-Type"] == "SubscriptionConfirmation":
            body = request.get_json(force=True)
            req = requests.get(body["SubscribeURL"])
            print(req.content)

    print(request.data)

    return "", 200


@bp.route('/endpoint-<string:short_uid>', methods=['DELETE'])
def delete_sns_endpoint(short_uid):
    rd.add_deleted_endpoint(short_uid)
    return "", 204


@bp.route('/endpoint-<string:short_uid>/logs', methods=['GET'])
def sns_endpoint_logs(short_uid):
    logs = rd.get_logs_from_endpoint(short_uid)
    return jsonify({'logs': logs})
