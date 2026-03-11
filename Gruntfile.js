module.exports = function (grunt) {
    grunt.initConfig({
        sass: {
            options: {
                implementation: require('sass'),
                sourceMap: true,
                api: 'modern'
            },
            dist: {
                files: {
                    'apps/assets/main.css': 'apps/assets/styles/main.scss',
                    'apps/assets/home_page.css': 'apps/assets/styles/home_page.scss',
                    'apps/assets/nav_bar.css': 'apps/assets/styles/nav_bar.scss',
                    'apps/assets/results.css': 'apps/assets/styles/results.scss',
                    'apps/assets/result.css': 'apps/assets/styles/result.scss',
                    'apps/assets/params_climatic.css': 'apps/assets/styles/params_climatic.scss',
                    'apps/assets/params_genetic.css': 'apps/assets/styles/params_genetic.scss',
                    'apps/assets/upload_page.css': 'apps/assets/styles/upload_page.scss',
                    'apps/assets/button.css': 'apps/assets/styles/utils/button.scss',
                    'apps/assets/popup.css': 'apps/assets/styles/utils/popup.scss',
                    'apps/assets/tooltip.css': 'apps/assets/styles/utils/tooltip.scss',
                    'apps/assets/help.css': 'apps/assets/styles/help.scss',
                    'apps/assets/toast.css': 'apps/assets/styles/utils/toast.scss',
                    'apps/assets/email_input.css': 'apps/assets/styles/utils/email_input.scss',
                    'apps/assets/result_card.css': 'apps/assets/styles/utils/result_card.scss',
                    'apps/assets/page_layout.css': 'apps/assets/styles/utils/page_layout.scss'
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
                    'apps/assets/styles/result.scss',
                    'apps/assets/styles/params_climatic.scss',
                    'apps/assets/styles/params_genetic.scss',
                    'apps/assets/styles/upload_page.scss',
                    'apps/assets/styles/utils/button.scss',
                    'apps/assets/styles/utils/popup.scss',
                    'apps/assets/styles/utils/tooltip.scss',
                    'apps/assets/styles/utils/table.scss',
                    'apps/assets/styles/help.scss',
                    'apps/assets/styles/utils/toast.scss',
                    'apps/assets/styles/utils/email_input.scss',
                    'apps/assets/styles/utils/result_card.scss',
                    'apps/assets/styles/utils/page_layout.scss'
                ],
                tasks: ['build-css']
            }
        }
    });

    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('build-css', ['sass']);
    grunt.registerTask('default', ['build-css', 'watch']);
};
