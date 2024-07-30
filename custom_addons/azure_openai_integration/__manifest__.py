{
    'name': 'Azure OpenAI Integration',
    'version': '1.0.0',
    'license': 'GPL-3',
    'summary': 'Azure OpenAI Integration',
    'description': 'This feature enables the application to utilize the capabilities of the GPT language model to generate human-like responses, enhancing the natural and intuitive user experience. It also supports customization options for prompts and token limits for each user, offering greater flexibility and optimizing costs.',
    'author': 'Dane',
    'maintainer': 'Dane',    
    'depends': ['base', 'base_setup', 'mail'],
    'data': [        
        'security/ir.model.access.csv',
        'data/user_partner_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml'
    ],    
    'installable': True,
    'application': False,
    'auto_install': False,
    'category': 'OpenAI',
    'price': '200',
    'currency': 'USD',
    'images': ['static/description/banner.png']
}
