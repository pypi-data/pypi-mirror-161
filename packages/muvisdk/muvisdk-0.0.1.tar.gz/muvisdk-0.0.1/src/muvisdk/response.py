def ok(response):
    return {
        'status': 'ok',
        'response': response
    }


def error(message):
    return {
        'status': 'error',
        'message': message
    }
