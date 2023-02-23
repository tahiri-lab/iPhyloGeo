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
                tasks: ['build-css']
            }
        }
    });

    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('build-css', ['sass']);
    grunt.registerTask('default', ['build-css','watch']);
};
