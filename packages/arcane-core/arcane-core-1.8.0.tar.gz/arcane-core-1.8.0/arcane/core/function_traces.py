import logging
import traceback


# Only because of a GCP issue: https://issuetracker.google.com/issues/155215191
def try_catch_log(wrapped_func):
    def wrapper(*args, **kwargs):
        try:
            response = wrapped_func(*args, **kwargs)
        except Exception as e:
            # Replace new lines with spaces so as to prevent several entries which
            # would trigger several errors.
            error_message = traceback.format_exc().replace('\n', '  ')
            logging.error(error_message)
            return ('Error', e)
        return response
    return wrapper
