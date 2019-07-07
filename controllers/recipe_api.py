import tempfile
import json

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
from gluon.utils import web2py_uuid

@auth.requires_login()
@auth.requires_signature()
def get_users_recipes():
	# Obtain the start and end index.
	start_index = int(request.vars.start_index) if request.vars.start_index is not None else 0
	end_index = int(request.vars.end_index) if request.vars.end_index is not None else 10	

	# Based off the request type, choose the appropriate base query.
	if request.vars.type == 'user':
		# Return recipes created by the user.
		query = (db.recipes.created_by == auth.user_id)
	elif request.vars.type == 'favorites':
		# Return recipes favorited by the user.
		query = ((db.favorites.favoriter == auth.user_id) & (db.recipes.id == db.favorites.recipe))
	else:
		# An unsupported type was provided. Raise an error.
		raise HTTP(500)

	# Retrieve the range of recipes from the database ordered in reverse chronological order.
	rows = db(query).select(db.recipes.ALL,
							limitby=(start_index, end_index),
							orderby=~db.recipes.created_on)

	# Append each retrieved recipe to recipes to be returned to the user.
	recipes = []
	for row in rows:
		# Retrieve the tags as strings instead of by their ids.
		tags = [tag['name'] for tag in db(db.tags.id.belongs(row.tags)).select().as_list()]

		# Update the quantities so that the '$$$' placeholder for empty string is returned
		# as an empty string.
		quantities = [quantity.replace('$$$', '') for quantity in row.quantities]

		recipe = dict(
			id = row.id,
			title = row.title,
			description = row.description,
			image_url = row.image_url,
			time_required = row.time_required,
			serving_size = row.serving_size,
			quantities = quantities,
			ingredients = row.ingredients,
			instructions = row.instructions,
			notes = row.notes,
			tags = tags,
		)

		if request.vars.type == 'favorites':
			# Obtain the user's rating.
			user_rating = db((db.user_ratings.rater == auth.user_id) &
						     (db.user_ratings.recipe == row.id)).select().first()
			recipe['user_rating'] = user_rating.rating if user_rating is not None else None

			# Obtain the total rating / vote count of the recipe.
			total_rating = db(db.total_ratings.recipe == row.id).select().first()
			recipe['total_score'] = total_rating.total_score if total_rating is not None else 0
			recipe['vote_count'] = total_rating.vote_count if total_rating is not None else 0
			print total_rating

			# Obtain the user's favorite status of the recipe.
			favorited = not db((db.favorites.favoriter == auth.user_id) &
						       (db.favorites.recipe == row.id)).isempty()
			recipe['favorited'] = favorited

		recipes.append(recipe)

	# Return the total number of related recipes back to the user.
	# - This should only be done once per query.
	# - The user should return this value to the server if it is the same query.
	total = int(request.vars.total) if request.vars.total is not None else db(query).count()

	return response.json(dict(
			recipes = recipes,
			total = total,
		))


@auth.requires_login()
@auth.requires_signature()
def add_recipe():
	# Parse json lists in the POST request back to a list. 
	quantities = json.loads(request.vars.quantities) if request.vars.quantities is not None else []
	ingredients = json.loads(request.vars.ingredients) if request.vars.ingredients is not None else []
	tags = json.loads(request.vars.tags) if request.vars.tags is not None else []

	# Insert each tag into the "tags" table so that they can be referenced by the recipe.
	tag_ids = []
	for tag in tags:
		tag_id = db.tags.update_or_insert(db.tags.name == tag, name = tag)
		if tag_id is None:
			# The tag has previously been inserted into the table.
			# Fetch the tag's id from the "tags" table.
			tag_id = db(db.tags.name == tag).select().first().id
		tag_ids.append(tag_id)

	# Process the "quantities" such that empty strings are represented as '$$$'
	quantities = [quantity or '$$$' for quantity in quantities]

	# Insert the recipe into the "recipes" table.
	recipe_id = db.recipes.insert(
		title = request.vars.title,
		description = request.vars.description,
		image_url = request.vars.image_url,
		time_required = request.vars.time_required,
		serving_size = request.vars.serving_size,
		quantities = quantities,
		ingredients = ingredients,
		instructions = request.vars.instructions,
		notes = request.vars.notes,
		tags = tag_ids,
	)

	# Create a corresponding entry in the "total_ratings" entry.
	db.total_ratings.insert(
		recipe = recipe_id,
	)

	# Return the added recipe back to the user.
	redirect(URL('default', 'recipes'))


@auth.requires_login()
@auth.requires_signature()
def update_recipe():
	# If no recipe id is provided, raise an error.
	recipe_id = request.vars.recipe_id
	if recipe_id is None:
		raise HTTP(500)

	# Return the recipe it exists and it belongs to the user.
	# Otherwise, raise an error.
	q = ((db.recipes.created_by == auth.user_id) & (db.recipes.id == recipe_id))
	recipe = db(q).select().first()
	if recipe is None:
		raise HTTP(500)

	# Parse json lists in the POST request back to a list. 
	quantities = json.loads(request.vars.quantities) if request.vars.quantities is not None else []
	ingredients = json.loads(request.vars.ingredients) if request.vars.ingredients is not None else []
	tags = json.loads(request.vars.tags) if request.vars.tags is not None else []

	# Insert each tag into the "tags" table so that they can be referenced by the recipe.
	tag_ids = []
	for tag in tags:
		tag_id = db.tags.update_or_insert(db.tags.name == tag, name = tag)
		if tag_id is None:
			# The tag has previously been inserted into the table.
			# Fetch the tag's id from the "tags" table.
			tag_id = db(db.tags.name == tag).select().first().id
		tag_ids.append(tag_id)

	# Process the "quantities" such that empty strings are represented as '$$$'
	quantities = [quantity or '$$$' for quantity in quantities]
	
	# Update the record.
	recipe.update_record(
		title = request.vars.title,
		description = request.vars.description,
		image_url = request.vars.image_url,
		time_required = request.vars.time_required,
		serving_size = request.vars.serving_size,
		quantities = quantities,
		ingredients = ingredients,
		instructions = request.vars.ingredients,
		notes = request.vars.notes,
		tags = tag_ids,
	)
	return 'ok'


@auth.requires_login()
@auth.requires_signature()
def delete_recipe():
	# If no recipe id is provided, raise an error.
	recipe_id = request.vars.recipe_id
	if recipe_id is None:
		raise HTTP(500)

	# Return the recipe it exists and it belongs to the user.
	# Otherwise, raise an error.
	q = ((db.recipes.created_by == auth.user_id) & (db.recipes.id == recipe_id))
	recipe = db(q).select().first()
	if recipe is None:
		raise HTTP(500)

	# Delete the recipe from the table.
	recipe.delete_record()
	return 'ok'


@auth.requires_login()
@auth.requires_signature()
def favorite_recipe():
	recipe_id = request.vars.recipe_id
	if recipe_id is None:
		# The recipe_id was not passed in. Raise an error.
		raise HTTP(500)

	# Store the user favoriting this recipe into the 'favorites' table.
	ret = db.favorites.validate_and_insert(recipe = recipe_id)
	if ret.errors:
		# The recipe does not exist. Raise an error.
		raise HTTP(500)
	return 'ok'


@auth.requires_login()
@auth.requires_signature()
def unfavorite_recipe():
	recipe_id = request.vars.recipe_id
	if recipe_id is None:
		# The recipe_id was not passed in. Raise an error.
		raise HTTP(500)

	# Delete the corresponding user's favorite.
	q = ((db.favorites.favoriter == auth.user_id) & (db.favorites.recipe == recipe_id))
	db(q).delete()

	return 'ok'
