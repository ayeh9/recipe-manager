# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime


def get_user_email():
    return auth.user.email if auth.user else None


# Table: recipes
# Stores the recipes submitted by users.
db.define_table('recipes',
				Field('created_by', 'reference auth_user', default=auth.user_id),
				Field('created_on', 'datetime', default=request.now),
				Field('updated_on', 'datetime', default=request.now, update=datetime.datetime.utcnow()),
				Field('is_public', 'boolean', default=False),
				Field('title'),
				Field('description', 'text'),
				Field('image_url'),
				Field('time_required'),
				Field('serving_size'),
				Field('quantities', 'list:string'),
				Field('ingredients', 'list:string'),
				Field('instructions', 'text'),
				Field('notes', 'text'),
				Field('tags', 'list:reference tags'))


# Table: tags
# Stores the tags that have been created by users.
# - Tags should be created before being referenced by a recipe.
db.define_table('tags',
				Field('name'))


# Table: user_ratings
# Stores the user's rating of a recipe.
# - The rating can be an integer from 1 to 5 (inclusive).
db.define_table('user_ratings',
				Field('rater', 'reference auth_user', default=auth.user_id),
				Field('recipe', 'reference recipes'),
				Field('rating', 'integer', requires=IS_INT_IN_RANGE(1, 6)))


# Table: total_ratings
# Stores each recipe's current rating by other users.
# - The rating can be calculated by total_score / vote_count.
db.define_table('total_ratings',
				Field('recipe', 'reference recipes'),
				Field('vote_count', 'integer', default=0, requires=IS_INT_IN_RANGE(0, 1e100)),
				Field('total_score', 'integer', default=0, requires=IS_INT_IN_RANGE(0, 1e100)))


# Table: favorites
# Stores the user's favorite recipes (from other users).
# - A user's favorited recipes should be included in their searches.
db.define_table('favorites',
				Field('favoriter', 'reference auth_user', default=auth.user_id),
				Field('recipe', 'reference recipes'),
				Field('favorited_on', 'datetime', default=request.now))


# Table: cookbooks
# Store the user's cookbooks names.
# - Cookbooks should be created before being referenced by a recipe.
db.define_table('cookbooks',
				Field('created_by', 'reference auth_user', default=auth.user_id),
				Field('created_on', 'datetime', default=request.now),
				Field('updated_on', 'datetime', default=request.now, update=datetime.datetime.utcnow()),
				Field('title'))


# Table: cookbook_assignments
# Store the assignments of recipes to user's cookbooks.
# - This is done as a separate table such that one can add their own recipes as well as
#   favorited recipes to the cookbook.
db.define_table('cookbook_assignments',
				Field('cookbook', 'reference cookbooks'),
				Field('recipe', 'reference recipes'),
				Field('added_on', 'datetime', default=request.now))


# after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)
