module.exports = function (grunt) {
    grunt.initConfig({
        sass: {
            options: {
                sourceMap: true,
                implementation: require('node-sass')
            },
            dist: {
                files: {
                    'assets/main.css': 'assets/scss/main.scss'
                }
            }
        },
        watch: {
            sass: {
                files: ['assets/scss/main.scss'],
                tasks: ['sass']
            }
        }
    });

    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['watch']);
};
