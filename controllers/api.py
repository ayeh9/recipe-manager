# Here go your api methods.

def is_logged_in():
	return response.json(dict(
		logged_in = auth.user is not None,
	))
