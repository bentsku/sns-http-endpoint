import ujson
import requests

from flask import request, Response, current_app
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
        body = request.data.decode() if "x-amz-sns-rawdelivery" in request.headers else request.get_json(force=True)
        log = {
            "headers": dict(request.headers.items()),
            "body": body
        }
        rd.add_logs_to_endpoint(token=short_uid, log_data=ujson.dumps(log))
        if request.headers["X-Amz-Sns-Message-Type"] == "SubscriptionConfirmation":
            rd.add_endpoint_as_pending(short_uid)
            if current_app.config["SNS_AUTO_SUBSCRIBE"]:
                body = request.get_json(force=True)
                try:
                    req = requests.get(body["SubscribeURL"])
                except requests.ConnectionError as e:
                    if "localhost" in str(e):
                        return bad_request("The SubscribeURL links to localhost domain, unreachable")
                    raise
                rd.del_endpoint_as_pending(short_uid)
                print(req.content)
        else:
            rd.del_endpoint_as_pending(short_uid)

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


@bp.route('/endpoint-<string:short_uid>/poll-logs', methods=['GET'])
def sns_endpoint_poll_logs(short_uid):
    logs = rd.get_len_logs_from_endpoint(short_uid)
    return jsonify({'logs_length': logs})


@bp.route('/pending-subscriptions', methods=['GET'])
def sns_endpoint_pending_subscriptions():
    pending_subs = rd.get_all_pending()
    return jsonify({'pending_subscriptions': pending_subs})
