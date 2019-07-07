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



    



    self.get_recipe = function() {
        $.getJSON(get_memos_url(0, 10), function (data) {
            self.vue.title = data.title;
            self.vue.description = data.description;
            self.vue.image_url = data.image_url;
            self.vue.time_required = data.time_required;
            self.vue.serving_size = data.serving_size;
            self.vue.quantities = data.quantities;
            self.vue.ingredients = data.ingredients;
            self.vue.notes = data.notes;
            self.vue.tags = data.tags;
        });
    }





    self.add_recipe = function () {
        // The submit button to add a memo has been added.
        $.post(add_recipe_url,
        {
            title: self.vue.recipe_title,
            description: self.vue.recipe_description,
            image_url: self.vue.recipe_image_url,
            time_required: self.vue.recipe_cooking_time,
            serving_size: self.vue.recipe_serving_size,

            quantities: JSON.stringify(self.vue.quantity),
            ingredients: JSON.stringify(self.vue.ingredient),

            instructions: self.vue.recipe_instructions,
            notes: self.vue.recipe_author_notes,

            tags:JSON.stringify(self.vue.tags),
        },
        function (data) {
            console.log(self.vue.recipe_title + " has been POSTed");
            document.location.href = my_recipes_home;
        });
    };



    self.edit_memo = function (memo_idx) {
        // Save the value, e.g. sending it to the server.
        self.vue.save_pending = true;
        var memo = self.vue.memos[memo_idx];

        $.post(edit_url,
            {title: self.vue.form_title,
             memo_id: memo.id,
             memo: self.vue.form_memo},
            function (data) {
                self.vue.save_pending = false;
                self.vue.is_editing = false;
                self.vue.editing_id = -1;
                self.vue.editing_idx = -1;
                $.web2py.enableElement($("#edit_memo_submit"));
                Vue.set(self.vue.memos, memo_idx, data.memo);
                enumerate(self.vue.memos);
            }
        );
    };

    self.add_ingredient_form = function() {
        if (self.vue.added_ingredient_name == '') {
            return;
        } else {
            console.log(self.vue.added_ingredient_name)
            console.log(self.vue.added_ingredient_quantity)
            self.vue.ingredients.push({ingredient: self.vue.added_ingredient_name, quantity: self.vue.added_ingredient_quantity});
            self.vue.ingredient.push(self.vue.added_ingredient_name),
            self.vue.quantity.push(self.vue.added_ingredient_quantity),
            self.vue.added_ingredient_name = '';
            self.vue.added_ingredient_quantity = '';
            return;
        }
    }


    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};


    self.delete_ingredient = function(ingredientss) {
        var index = self.vue.ingredient.indexOf(ingredientss);
        self.vue.ingredient.splice(index, index + 1);
        self.vue.quantity.splice(index, index + 1);

        enumerate(self.vue.ingredient);
        enumerate(self.vue.quantity);
        console.log("Removing " + ingredientss + " at " + index);

        return;
    }


    self.add_tag_form = function() {
        if (self.vue.added_tag == '') {
            return;
        } else {
            self.vue.tags.push(self.vue.added_tag);
            self.vue.added_tag = '';
            return;
        }
    }



    self.upload_file = function (event) {
        // Reads the file.
        var input = event.target;
        var file_input = document.getElementById('file_input');
        var file = input.files[0];

        if (file) {
            // First, gets an upload URL.
            console.log("Trying to get the upload url");
            $.getJSON('https://popollo183.appspot.com/uploader/uploader/get_upload_url',
                function (data) {
                    // We now have upload (and download) URLs.
                    var put_url = data['signed_url'];
                    var get_url = data['access_url'];
                    console.log("Received upload url: " + put_url);
                    // Uploads the file, using the low-level interface.
                    var req = new XMLHttpRequest();
                    req.addEventListener("load", self.upload_complete(get_url));
                    // TODO: if you like, add a listener for "error" to detect failure.
                    req.open("PUT", put_url, true);
                    req.send(file);
                });
        }
    };


    self.upload_complete = function(get_url) {
        console.log('The file was uploaded; it is now available at ' + get_url);
        // TODO: The file is uploaded.  Now you have to insert the get_url into the database, etc.

            setTimeout(function(){
                self.vue.recipe_image_url = get_url;    
            }, 1000);
    
    };


    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            is_adding: true,
            is_editing: false,
            is_viewing: false,

            recipe_title: '',
            recipe_description: '',
            recipe_image_url: '',
            recipe_cooking_time: '',
            recipe_serving_size: '',


            added_ingredient_name: '',
            added_ingredient_quantity: '',
            added_tag: '',


            recipe_instructions: '',
            recipe_author_notes: '',




            ingredients: [],

            ingredient: [],
            quantity: [],
            tags: [],
        },
        methods: {
            add_recipe : self.add_recipe,
            edit_recipe : self.edit_recipe,

            add_ingredient_form: self.add_ingredient_form,
            add_tag_form: self.add_tag_form,
            delete_ingredient: self.delete_ingredient,

            upload_file: self.upload_file,
            upload_complete: self.upload_complete,
            update_image: self.update_image,



        }

    });


    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});
