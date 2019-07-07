import tempfile
import json

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
from gluon.utils import web2py_uuid

@auth.requires_login()
@auth.requires_signature()
def add_ratings():
	# Validate the input.
	if request.vars.recipe_id is None or request.vars.rating is None:
		# Either the recipe id or rating was not passed in.
		raise HTTP(500)

	# Validate that the "rating" is an integer. Raise an error if it isn't.
	recipe_id = request.vars.recipe_id
	try:
		rating = int(request.vars.rating)
	except:
		raise HTTP(500)

	# Validate and insert the rating into the "user_ratings" table.
	ret = db.user_ratings.validate_and_insert(
		recipe = request.vars.recipe_id,
		rating = request.vars.rating,
	)

	# If there are errors, raise an error.
	if ret.errors:
		raise HTTP(500)

	# Otherwise, update the "total_ratings" with this new rating.
	recipe_ratings = db(db.total_ratings.recipe == recipe_id).select().first()
	if recipe_ratings:
		# This recipe already had ratings. Update its total.
		recipe_ratings.total_score += rating
		recipe_ratings.vote_count += 1
		recipe_ratings.update_record()
	else:
		# This recipe has no ratings. Initialize its ratings count.
		db.total_ratings.insert(
			recipe = recipe_id,
			total_score = rating,
			vote_count = 1,
		)

	return 'ok'

@auth.requires_login()
@auth.requires_signature()
def update_ratings():
	# Validate the input.
	if request.vars.recipe_id is None or request.vars.new_rating is None \
	   or request.vars.old_rating is None:
		# Either the recipe id or rating was not passed in.
		raise HTTP(500)

	# Validate that the "rating" is an integer. Raise an error if it isn't.
	recipe_id = request.vars.recipe_id
	try:
		old_rating = int(request.vars.old_rating)
		new_rating = int(request.vars.new_rating)
	except:
		raise HTTP(500)

	# Validate the new_rating is legal.
	if new_rating < 1 or new_rating > 5:
		raise HTTP(500)

	q = ((db.user_ratings.rater == auth.user_id) & (db.user_ratings.recipe == recipe_id))
	user_ratings = db(q).select().first()
	if user_ratings is None:
		raise HTTP(500)

	# Update the user's rating of the recipe.
	# Raise an error if the new_rating is invalid.
	user_ratings.update_record(rating = new_rating)

	# Update the recipe's rating counts in the "total_ratings" table.
	recipe_ratings = db(db.total_ratings.recipe == recipe_id).select().first()
	recipe_ratings.total_score -= old_rating
	recipe_ratings.total_score += new_rating
	recipe_ratings.update_record()

	return 'ok' 