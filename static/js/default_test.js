// This is the js for the default/index.html view.

var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    var recipe_image_link = 'https://storage.googleapis.com/popollo-images/fa227445-4a48-4491-9629-b948e1600448.jpg?Expires=1560154318&GoogleAccessId=popollo-image-uploader%40popollo183.iam.gserviceaccount.com&Signature=OUTX01rDmnjj2ns6NnhgYXgaVMA3GkxxD6SyFjfrk3kx%2FpKBprzhHpy5%2FDtZZ33fF5iFCGEVuQ8seLsEoRhFzjvrdeFKRWNSPB6CtDXrLltZZ7LdwFi5oRf4TF7KQXCf7nsVxIQO6eLLo%2B7Ge7WmNE94gK3EbKybpG8v%2B68GEfuPcOOzDOAz66gLN020g8eRmQennaqEr04jaSCa5Gc6Norew4jZtCtfr9u4ktUvSock%2BffmHOsHuhoHur9SAfkQdpOx9z15NsHPCwYxQBD5PVM6Me1%2FJ29SCUBAkqQ3HpzioequdPSYWMSKhA9sRWta3WTyqsMoG8LxeF%2BVz1vX2w%3D%3D';

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};


    self.test_add_recipe = function() {
        var recipe = {
            title: 'Scrambled Eggs',
            description: 'Delicious and fluffy, yet simpled, scrambled eggs!',
            image_url: recipe_image_link,
            time_required: '5 minutes',
            serving_size: '1',
            quantities: ['1', '1 pinch', '1 pinch', ''],
            ingredients: ['egg', 'salt', 'black pepper', 'ketchup'],
            instructions: 'These are some instructions hahahahahahaha',
            notes: '',
            tags: ['egg', 'breakfast', 'easy'],
        };

        $.post(add_recipe_url,
        {
            title: 'Scrambled Eggs',
            description: 'Delicious and fluffy, yet simpled, scrambled eggs!',
            image_url: recipe_image_link,
            time_required: '5 minutes',
            serving_size: '1',
            quantities: JSON.stringify(recipe.quantities),
            ingredients: JSON.stringify(recipe.ingredients),
            instructions: 'These are some instructions hahahahahahaha',
            notes: '',
            tags: JSON.stringify(recipe.tags),            
        },
        function(data) {
            console.log(data.added_recipe);
        });
    }

    self.test_has_recipes = function() {
        $.getJSON(has_recipes_url,
            function(data) {
                console.log(data.has_recipes);
            });
    }

    self.test_favorite_recipe = function() {
        $.post(favorite_recipe_url,
        {
            recipe_id: 1,          
        },
        function(data) {
            console.log(data);
        });
    }

    self.test_unfavorite_recipe = function() {
        $.post(unfavorite_recipe_url,
        {
            recipe_id: 1,          
        },
        function(data) {
            console.log(data);
        });
    }

    self.test_search_users_recipes = function() {
        $.getJSON(search_recipes_url,
        {
            type: 'favorites',
            start_index: 0,
            end_index: 10,
            search_term: 'scrambled',
            inclusions: JSON.stringify(['EGG']),
            exclusions: JSON.stringify([]),
        }, function(data) {
            console.log(data.recipes);
            console.log(data.total);
        });
    }

    self.test_rating_recipes = function() {
        $.post(rate_recipe_url,
        {
            recipe_id: 1,
            rating: 1,
        },
        function(data) {
            console.log(data);
        });  
    }

    self.test_rerating_recipes = function() {
        $.post(rerate_recipe_url,
        {
            recipe_id: 1,
            old_rating: 3,
            new_rating: 4,
        },
        function(data) {
            console.log(data);
        });  
    }

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {

        },
        methods: {
            test_add_recipe: self.test_add_recipe,
            test_has_recipes: self.test_has_recipes,
            test_favorite_recipe: self.test_favorite_recipe,
            test_unfavorite_recipe: self.test_unfavorite_recipe,
            test_search_users_recipes: self.test_search_users_recipes,
            test_rating_recipes: self.test_rating_recipes,
            test_rerating_recipes: self.test_rerating_recipes,
        }
    });

    $("#vue-div").show();

    return self;
};

var APP = null;


// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
