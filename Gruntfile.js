module.exports = function (grunt) {
    grunt.initConfig({
        sass: {
            options: {
                sourceMap: true,
                implementation: require('node-sass')
            },
            dist: {
                files: {
                    'assets/main.css': 'assets/styles/main.scss',
                    'assets/home_page.css': 'assets/styles/home_page.scss',
                    'assets/nav_bar.css': 'assets/styles/nav_bar.scss',
                    'assets/results.css': 'assets/styles/results.scss',
                    'assets/upload_page.css': 'assets/styles/upload_page.scss',
                    'assets/helper.css': 'assets/styles/utils/helper.scss',
                    'assets/button.css': 'assets/styles/utils/button.scss'
                }
            }
        },
        watch: {
            sass: {
                files: [
                    'assets/styles/main.scss',
                    'assets/styles/home_page.scss',
                    'assets/styles/nav_bar.scss',
                    'assets/styles/results.scss',
                    'assets/styles/upload_page.scss',
                    'assets/styles/utils/helper.scss',
                    'assets/styles/utils/button.scss',
                ],
                tasks: ['build-css']
            }
        }
    });

    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('build-css', ['sass']);
    grunt.registerTask('default', ['build-css','watch']);
};
