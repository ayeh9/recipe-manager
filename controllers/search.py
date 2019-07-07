import json

# Cloud-safe of uuid, so that many cloned servers do not all use the same uuids.
from gluon.utils import web2py_uuid

@auth.requires_login()
@auth.requires_signature()
def has_users_recipes():
	# Query: Has the user created recipes?
	query = ((db.recipes.created_by == auth.user_id)) 
	has_created_recipes = not db(query).isempty()

	# Query: Has the user favorited recipes?
	query2 = ((db.favorites.favoriter == auth.user_id) & (db.recipes.id == db.favorites.recipe))
	has_favorited_recipes = not db(query2).isempty()

	# Return if the user has created or favorited recipes.
	has_recipes = has_created_recipes or has_favorited_recipes
	return response.json(dict(
			has_recipes = has_recipes,
		))

@auth.requires_login()
@auth.requires_signature(hash_vars=False)
def users_recipes():
	# Obtain the start and end index of the search.
	start_index = int(request.vars.start_index) if request.vars.start_index is not None else 0
	end_index = int(request.vars.end_index) if request.vars.end_index is not None else 10

	# Obtain the set of possible filters (search term, included ingredients, excluded ingredients).
	search_term = request.vars.search_term
	inclusions = json.loads(request.vars.inclusions) if request.vars.inclusions is not None else []
	exclusions = json.loads(request.vars.exclusions) if request.vars.exclusions is not None else []

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

	# Include the recipe only if its title contains the search term.
	if search_term is not None:
		query = (query & db.recipes.title.lower().contains(search_term.lower()))

	# Include the recipe only if it has all the included ingredients.
	for included_ingredient in inclusions:
		print included_ingredient
		query = (query & db.recipes.ingredients.lower().contains(included_ingredient.lower()))

	# Include the recipe only if it does not include the excluded ingredients.
	for excluded_ingredient in exclusions:
		query = (query & ~db.recipes.ingredients.lower().contains(excluded_ingredient.lower()))

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
		print quantities

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
@auth.requires_signature(hash_vars=False)
def browse_recipes():
	# Obtain the start and end index of the search.
	start_index = int(request.vars.start_index) if request.vars.start_index is not None else 0
	end_index = int(request.vars.end_index) if request.vars.end_index is not None else 10

	# Obtain the set of possible filters (search term, included ingredients, excluded ingredients).
	search_term = request.vars.search_term
	inclusions = json.loads(request.vars.inclusions) if request.vars.inclusions is not None else []
	exclusions = json.loads(request.vars.exclusions) if request.vars.exclusions is not None else []

	# Return recipes created by other users.
	query = (db.recipes.created_by != auth.user_id)

	# If "exclude_favorites" is included as an argument, filter out recipes that have been
	# favorited by the user.
	if request.vars.exclude_favorites is not None:
		# Obtain the list of recipes that the user has favorited.
		favorites_rows = db(db.favorites.favoriter == auth.user_id).select(db.favorites.recipe).as_list()
		favorites = [row['recipe'] for row in favorites_rows]

		# Filter out recipes already favorited by the user.
		query = (query & ~db.recipes.id.belongs(favorites))

	# Include the recipe only if its title contains the search term.
	if search_term is not None:
		query = (query & db.recipes.title.lower().contains(search_term.lower()))

	# Include the recipe only if it has all the included ingredients.
	for included_ingredient in inclusions:
		query = (query & db.recipes.ingredients.lower().contains(included_ingredient.lower()))

	# Include the recipe only if it does not include the excluded ingredients.
	for excluded_ingredient in exclusions:
		query = (query & ~db.recipes.ingredients.lower().contains(excluded_ingredient.lower()))

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
