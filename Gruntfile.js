module.exports = function (grunt) {
    grunt.initConfig({
        sass: {
            options: {
                sourceMap: true,
                implementation: require('node-sass')
            },
            dist: {
                files: {
                    'apps/assets/main.css': 'apps/assets/styles/main.scss',
                    'apps/assets/home_page.css': 'apps/assets/styles/home_page.scss',
                    'apps/assets/nav_bar.css': 'apps/assets/styles/nav_bar.scss',
                    'apps/assets/results.css': 'apps/assets/styles/results.scss',
                    'apps/assets/params_climatic.css': 'apps/assets/styles/params_climatic.scss',
                    'apps/assets/params_genetic.css': 'apps/assets/styles/params_genetic.scss',
                    'apps/assets/upload_page.css': 'apps/assets/styles/upload_page.scss',
                    'apps/assets/helper.css': 'apps/assets/styles/utils/helper.scss',
                    'apps/assets/button.css': 'apps/assets/styles/utils/button.scss'
                }
            }
        },
        watch: {
            sass: {
                files: [
                    'apps/assets/styles/main.scss',
                    'apps/assets/styles/home_page.scss',
                    'apps/assets/styles/nav_bar.scss',
                    'apps/assets/styles/results.scss',
                    'apps/assets/styles/params_climatic.scss',
                    'apps/assets/styles/params_genetic.scss',
                    'apps/assets/styles/upload_page.scss',
                    'apps/assets/styles/utils/helper.scss',
                    'apps/assets/styles/utils/button.scss',
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
