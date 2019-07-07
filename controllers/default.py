# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict(message=T('Index Page'))


@auth.requires_login()
def recipes():
    return dict(message=T('Recipes Page'))


@auth.requires_login()
def browse():
    return dict(message=T('Browse Page'))

@auth.requires_login()
def add_form():
    return dict(message=T('Add Recipe Page'))

@auth.requires_login()
def edit_form():
    # If no recipe id is provided, raise an error.
    recipe_id = request.vars.recipe_id
    if recipe_id is None:
        raise HTTP(500)

    # Retrieve the record from the database.
    recipe = db.recipes(recipe_id)
    if recipe is None:
        raise HTTP(500)

    # Only the creator should be able to edit.
    if auth.user_id != recipe.created_by:
        raise HTTP(500)

    # Retrieve the tags as strings instead of by their ids.
    tags = [tag['name'] for tag in db(db.tags.id.belongs(recipe.tags)).select().as_list()]
    recipe['tags'] = tags

    # Update the quantities so that the '$$$' placeholder for empty string is returned
    # as an empty string.
    quantities = [quantity.replace('$$$', '') for quantity in recipe.quantities]
    recipe['quantities'] = quantities

    return (dict(
            message=T('Edit Recipe Page'),
            recipe=recipe,
        ))


@auth.requires_login()
def recipe():
    # If no recipe id is provided, raise an error.
    recipe_id = request.vars.recipe_id
    if recipe_id is None:
        raise HTTP(500)

    # Retrieve the record from the database.
    recipe = db.recipes(recipe_id)
    if recipe is None:
        raise HTTP(500)

    # Retrieve the tags as strings instead of by their ids.
    tags = [tag['name'] for tag in db(db.tags.id.belongs(recipe.tags)).select().as_list()]
    recipe['tags'] = tags

    # Update the quantities so that the '$$$' placeholder for empty string is returned
    # as an empty string.
    quantities = [quantity.replace('$$$', '') for quantity in recipe.quantities]
    recipe['quantities'] = quantities

    # If the user did not create the recipe, grab additional information
    # such as ratings and favorited status.
    if auth.user_id != recipe.created_by:
        # Obtain the user's rating.
        user_rating = db((db.user_ratings.rater == auth.user_id) &
                         (db.user_ratings.recipe == recipe.id)).select().first()
        recipe['user_rating'] = user_rating.rating if user_rating is not None else None

        # Obtain the total rating / vote count of the recipe.
        total_rating = db(db.total_ratings.recipe == recipe.id).select().first()
        recipe['total_score'] = total_rating.total_score if total_rating is not None else 0
        recipe['vote_count'] = total_rating.vote_count if total_rating is not None else 0
        print total_rating

        # Obtain the user's favorite status of the recipe.
        favorited = not db((db.favorites.favoriter == auth.user_id) &
                           (db.favorites.recipe == recipe.id)).isempty()
        recipe['favorited'] = favorited

    return (dict(
            message=T('Recipe Page'),
            recipe=recipe,
        ))


def test():
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


