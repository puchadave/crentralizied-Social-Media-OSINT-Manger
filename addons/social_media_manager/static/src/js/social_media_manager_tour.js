odoo.define('social_media_manager.tour', function (require) {
    'use strict';

    const tour = require('web_tour.tour');

    tour.register('social_media_manager_tour', {
        test: true,
        url: '/web',
    }, [
        {
            content: 'Open the main menu',
            trigger: '.o_app[data-menu-xmlid="marketing_automation.menu_marketing_root"]',
        },
        {
            content: 'Open Social Media Manager',
            trigger: 'a[data-menu-xmlid="social_media_manager.menu_social_media_manager_root"]',
        },
        {
            content: 'Open Posts menu',
            trigger: 'a[data-menu-xmlid="social_media_manager.menu_social_media_post"]',
        },
        {
            content: 'Create a post',
            trigger: '.o_list_button_add',
        },
        {
            content: 'Set post name',
            trigger: 'input[name="name"]',
            run: 'text(Test Post)',
        },
        {
            content: 'Select account',
            trigger: 'div[name="account_id"] input',
            run: function () {},
        },
        {
            content: 'Save post',
            trigger: '.o_form_button_save',
        },
    ]);
});
