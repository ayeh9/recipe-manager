import tempfile
import json

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
from gluon.utils import web2py_uuid

@auth.requires_login()
@auth.requires_signature()
def create_cookbook():
	# Validate that a title for the cookbook has been passed in.
	cookbook_title = request.vars.title
	if cookbook_title is None:
		# The title does not exist. Raise an error.
		raise HTTP(500)

	# Create an entry for this cookbook in the "cookbooks" table.
	cookbook_id = db.cookbooks.insert(title = cookbook_title)

	# Return the new cookbook record back to the user.
	cookbook = db.cookbooks(cookbook_id)
	return response.json(dict(added_cookbook=cookbook))
