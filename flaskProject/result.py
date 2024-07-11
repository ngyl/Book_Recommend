from flask import jsonify


class Result:

    @staticmethod
    def ok(message, data=None):
        response = {
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), 200

    @staticmethod
    def fail(message):
        return jsonify({
            'message': message
        }), 400
