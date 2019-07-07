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

    var does_user_have_recipes = function() {
        $.getJSON(has_recipes_url,
            function(data) {
                self.vue.has_recipes = data.has_recipes;
                if (self.vue.has_recipes) {
                    search_recipes('user', 1);
                    search_recipes('favorites', 1);
                }
                $("#vue-div").show();
            }
        );
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

    var search_recipes = function(target, selected_page) {
        // Invalid target or selected_page argument.
        if (selected_page < 1) return;
        if (target != 'user' && target != 'favorites') return;

        // Set the target page.
        var target_page;
        if (target == 'user') {
            target_page = self.vue.users_results;
        } else {
            target_page = self.vue.favs_results;
        }

        // Define the arguments that will be sent to the server.
        var vars = {
            type: target,
            start_index: 10 * (selected_page - 1),
            end_index: 10 * (selected_page),
        }

        if (target_page.total != -1) {
            vars.total = target_page.total;
        }

        Vue.set(target_page, 'is_searching', true);
        $.getJSON(search_recipes_url, vars, function(data) {
            console.log(data);
            // Set is_searching to false.
            Vue.set(target_page, 'is_searching', false);

            // Set the recipes to the new recipes.
            Vue.set(target_page, 'recipes', data.recipes);
            if (target =='favorites') {
                stars_displayed(target_page['recipes']);
            }
            enumerate(target_page['recipes']);

            // Set the ${start} - ${end} of ${total} message.
            Vue.set(target_page, 'total', data.total);
            Vue.set(target_page, 'start_index', 10 * (selected_page - 1) + 1);
            if (target_page.total < 10 * selected_page) {
                Vue.set(target_page, 'end_index', data.total);
            } else {
                Vue.set(target_page, 'end_index', 10 * selected_page);
            }
        });
    }

    var goto_results_page = function() {
        reset_search_results();        
        self.vue.on_results_page = true;
        self.vue.inclusions_string = ingredients_as_string(self.vue.inclusions);
        self.vue.exclusions_string = ingredients_as_string(self.vue.exclusions);
    }

    self.get_recipe_url = function(recipe_id) {
        var pp = {
            recipe_id: recipe_id,
        };
        return recipe_url + "?" + $.param(pp);
    }

    self.switch_tabs = function(new_page) {
        self.vue.current_tab = new_page;
    }

    self.prev_page = function(target) {
        if (target == 'user') {
            if (self.vue.users_results.page_number == 1) {
                return;
            }
            self.vue.users_results.page_number -= 1;
            search_recipes(target, self.vue.users_results.page_number);
        } else if (target == 'favorites') {
            if (self.vue.favs_results.page_number == 1) {
                return;
            }
            self.vue.favs_results.page_number += 1;
            search_recipes(target, self.vue.favs_results.page_number);
        }
    }


    self.next_page = function(target) {
        if (target == 'user') {
            self.vue.users_results.page_number += 1;
            search_recipes(target, self.vue.users_results.page_number);
        } else if (target == 'favorites') {
            self.vue.favs_results.page_number += 1;
            search_recipes(target, self.vue.favs_results.page_number);
        }
    }


    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            // Determines what page the user is on.
            has_recipes: false,
            current_tab: 0,
            users_results: {
                is_searching: false,
                page_number: 1,
                total: -1,
                start_index: 0,
                end_index: 10,
                recipes: [],
            },
            favs_results: {
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
            switch_tabs: self.switch_tabs,
            prev_page: self.prev_page,
            next_page: self.next_page,
            get_recipe_url: self.get_recipe_url,
        }
    });

    does_user_have_recipes();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
