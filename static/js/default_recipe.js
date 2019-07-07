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

    var obtain_vue_data = function() {
        self.vue.recipe_id = Number($('#recipe_id').val());
        self.vue.favorited = $('#recipe_favorited').val();
        if (self.vue.favorited == 'True') {
            self.vue.favorited = true;
        } else {
            self.vue.favorited = false;
        }
        self.vue.user_rating = Number($('#recipe_user_rating').val());
        self.vue.total_score = Number($('#recipe_total_score').val());
        self.vue.vote_count = Number($('#recipe_vote_count').val());
    }

    self.favorite_recipe = function() {
        if (self.vue.favorited) {
            return;
        }

        $.post(favorite_recipe_url,
            { recipe_id: self.vue.recipe_id },
            function(data) {
                self.vue.favorited = true;
            }
        );
    }

    self.unfavorite_recipe = function() {
        if (!self.vue.favorited) {
            return;
        }

        $.post(unfavorite_recipe_url,
            { recipe_id: self.vue.recipe_id },
            function(data) {
                self.vue.favorited = false;
            }
        );
    }

    var stars_displayed = function() {
        if (self.vue.user_rating != 0) {
            self.vue.stars_displayed = self.vue.user_rating;
        } else if (self.vue.vote_count > 0) {
            self.vue.stars_displayed = Math.round(self.vue.total_score / self.vue.vote_count);
        } else {
            self.vue.stars_displayed = 0;
        }
    }

    self.mouseover_stars = function(index) {
        Vue.set(self.vue, 'stars_displayed', index);
    }

    self.mouseout_stars = function() {
        stars_displayed();
    }

    self.set_rating = function(index) {
        if (self.vue.user_rating == 0) {
            $.post(rate_recipe_url,
            {
                recipe_id: self.vue.recipe_id,
                rating: index,
            },
            function(data) {
                self.vue.user_rating = index;
                console.log(data);
            });
        } else {
            $.post(rerate_recipe_url,
            {
                recipe_id: self.vue.recipe_id,
                old_rating: self.vue.user_rating,
                new_rating: index,
            },
            function(data) {
                self.vue.user_rating = index;
            });            
        }
    }


    self.delete_recipe = function() {
        $.post(delete_recipe_url,
        {
            recipe_id: self.vue.recipe_id,
        },
        function(data) {
            window.close();
        });        
    }

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            recipe_id: null,
            favorited: null,
            user_rating: null,
            total_score: null,
            vote_count: null,
            stars_displayed: 0,
        },
        filters: {
        },
        methods: {
            favorite_recipe: self.favorite_recipe,
            unfavorite_recipe: self.unfavorite_recipe,
            update_stars_displayed: self.mouseover_stars,
            mouseout_stars: self.mouseout_stars,
            set_rating: self.set_rating,
            delete_recipe: self.delete_recipe,
        }
    });

    obtain_vue_data();

    stars_displayed();

    $("#vue-div").show();

    return self;
};



var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
