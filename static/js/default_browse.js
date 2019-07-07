// This is the js for the default/index.html view.

var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};

    var ingredients_as_JSON = function(list) {
        var ingredients = [];
        for (var i = 0; i < list.length; i++) {
            var ingredient = list[i].name;
            ingredients.push(ingredient);
        }
        return JSON.stringify(ingredients);
    }

    var ingredients_as_string = function(list) {
        var string = ''
        for (var i = 0; i < list.length; i++) {
            if (i == list.length - 1) {
                string += list[i].name;
            } else {
                string += (list[i].name + ', ');
            }
        }
        return string;
    }

    var stars_displayed = function(list) {
        for (var i = 0; i < list.length; i++) {
            var recipe = list[i];
            if (recipe.user_rating != null) {
                recipe.stars_displayed = recipe.user_rating;
            } else if (recipe.vote_count > 0) {
                recipe.stars_displayed = Math.round(recipe.total_score / recipe.vote_count);
            } else {
                recipe.stars_displayed = 0;
            }
        }
    }

    var search_recipes = function(selected_page) {
        // Invalid target or selected_page argument.
        if (selected_page < 1) return;

        // Define the arguments that will be sent to the server.
        var vars = {
            start_index: 10 * (selected_page - 1),
            end_index: 10 * (selected_page),
            inclusions: ingredients_as_JSON(self.vue.inclusions),
            exclusions: ingredients_as_JSON(self.vue.exclusions),
        }

        if (self.vue.results.total != -1) {
            vars.total = target_page.total;
        }

        if (self.vue.exclude_favorites == true) {
            vars.exclude_favorites = true;
        }

        Vue.set(self.vue.results, 'is_searching', true);
        $.getJSON(browse_recipes_url, vars, function(data) {
            // Set is_searching to false.
            Vue.set(self.vue.results, 'is_searching', false);

            // Set the recipes to the new recipes.
            Vue.set(self.vue.results, 'recipes', data.recipes);
            stars_displayed(self.vue.results.recipes);
            enumerate(self.vue.results.recipes);

            // Set the ${start} - ${end} of ${total} message.
            Vue.set(self.vue.results, 'total', data.total);
            Vue.set(self.vue.results, 'start_index', 10 * (selected_page - 1) + 1);
            if (self.vue.results.total < 10 * selected_page) {
                Vue.set(self.vue.results, 'end_index', data.total);
            } else {
                Vue.set(self.vue.results, 'end_index', 10 * selected_page);
            }
        });
    }

    // Returns if the list is empty.
    self.is_empty = function(list) {
        return list.length == 0;
    }

    self.add_ingredient = function(list) {
        // Do nothing if no search term is present.
        if (self.vue.search_term == '') {
            return;
        } 

        // Determine whether we are adding to "inclusions" or "exclusions"
        // Add the new ingredient to the corresponding list.
        if (list == 'inclusions') {
            self.vue.inclusions.push({name: self.vue.search_term});
            enumerate(self.vue.inclusions);
        } else if (list == 'exclusions') {
            self.vue.exclusions.push({name: self.vue.search_term});
            enumerate(self.vue.exclusions);
        }

        // Clear the search term from the search bar.
        self.vue.search_term = '';
    }

    self.remove_ingredient = function(list, index) {
        // Determine whether we are removing from "inclusions" or "exclusions"
        // Remove the target ingredient and re-enumerate the list.
        if (list == 'inclusions') {
            self.vue.inclusions.splice(index, 1);
            enumerate(self.vue.inclusions);
        } else if (list == 'exclusions') {
            self.vue.exclusions.splice(index, 1);
            enumerate(self.vue.exclusions);
        }
    }

    var reset_search_results = function() {
        self.vue.results = {
            is_searching: false,
            page_number: 1,
            total: -1,
            start_index: 0,
            end_index: 10,
            recipes: [],            
        };
    }

    var goto_results_page = function() {
        reset_search_results();
        self.vue.on_results_page = true;
        self.vue.inclusions_string = ingredients_as_string(self.vue.inclusions);
        self.vue.exclusions_string = ingredients_as_string(self.vue.exclusions);
    }

    self.toggle_exclude_favorites = function() {
        self.vue.exclude_favorites = !self.vue.exclude_favorites;
    }

    self.search = function() {
        goto_results_page();
        search_recipes(1);
    }

    self.back = function() {
        // Return to the search page.
        self.vue.on_results_page = false;

        // Reset the results page's variables.
        reset_search_results();
    }

    self.prev_page = function() {
        if (self.vue.results.page_number == 1) {
            return;
        }
        self.vue.results.page_number += 1;
        search_recipes(self.vue.results.page_number);
    }


    self.next_page = function() {
        self.vue.results.page_number += 1;
        search_recipes(results.page_number);
    }

    self.favorite_recipe = function(recipe_index) {
        var recipe = self.vue.results.recipes[recipe_index];
        if (recipe.favorited) {
            return;
        }

        $.post(favorite_recipe_url,
            { recipe_id: recipe.id },
            function(data) {
                console.log(data);
                Vue.set(self.vue.results.recipes[recipe_index], 'favorited', true);
            }
        );
    }


    self.unfavorite_recipe = function(recipe_index) {
        var recipe = self.vue.results.recipes[recipe_index];
        if (!recipe.favorited) {
            return;
        }

        $.post(unfavorite_recipe_url,
            { recipe_id: recipe.id },
            function(data) {
                console.log(data);
                Vue.set(self.vue.results.recipes[recipe_index], 'favorited', false);
            }
        );
    }


    self.get_recipe_url = function(recipe_id) {
        var pp = {
            recipe_id: recipe_id,
        };
        return recipe_url + "?" + $.param(pp);
    };


    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            // Determines what page the user is on.
            on_results_page: false,

            // Search Conditions
            inclusions: [],
            exclusions: [],
            inclusions_string: '',
            exclusions_string: '',

            // Search Page Variables
            search_term: '',
            exclude_favorites: false,

            // Results Page Variables
            results: {
                is_searching: false,
                page_number: 1,
                total: -1,
                start_index: 0,
                end_index: 10,
                recipes: [],
            },
        },
        filters: {
            truncate: function (text, stop, clamp) {
                return text.slice(0, stop) + (stop < text.length ? clamp || '...' : '')
            },
        },
        methods: {
            is_empty: self.is_empty,
            toggle_exclude_favorites: self.toggle_exclude_favorites,
            add_ingredient: self.add_ingredient,
            remove_ingredient: self.remove_ingredient,
            search: self.search,
            back: self.back,
            prev_page: self.prev_page,
            next_page: self.next_page,
            favorite_recipe: self.favorite_recipe,
            unfavorite_recipe: self.unfavorite_recipe,
            get_recipe_url: self.get_recipe_url,
        }
    });

    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
