# Django API Hub - Custom Admin UI

A modern, intuitive admin interface for Django API Hub built with Tailwind CSS and Alpine.js.

## Features

- **Modern UI**: Clean, intuitive interface inspired by Steve Jobs' design philosophy
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dashboard**: Overview of system status and recent activity
- **Interactive Components**: Dynamic UI elements with Alpine.js and HTMX
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Custom Styling**: Extended Tailwind with custom components and utilities

## Architecture

The custom admin UI is built on top of Django's authentication system but replaces the default admin interface with a more user-friendly design. It follows these principles:

1. **Simplicity**: Focus on what matters, eliminate complexity
2. **Intuitiveness**: Design that feels natural and requires minimal learning
3. **Focus**: Highlight the most important actions and information
4. **Elegance**: Clean, minimal design with attention to detail
5. **Purpose**: Every element serves a clear purpose

## Technology Stack

- **Django**: Web framework for the backend
- **Tailwind CSS**: Utility-first CSS framework
- **Alpine.js**: Lightweight JavaScript framework for interactivity
- **HTMX**: HTML extensions for AJAX, CSS Transitions, and WebSockets
- **Inter & JetBrains Mono**: Modern, readable fonts

## Directory Structure

```
admin_ui/
├── static/
│   ├── admin_ui/
│   │   ├── css/
│   │   │   └── custom.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── img/
├── templates/
│   ├── admin_ui/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard/
│   │   │   ├── index.html
│   │   │   └── system_status.html
│   │   ├── includes/
│   │   │   └── sidebar_nav.html
│   │   ├── message_sources/
│   │   ├── api_connections/
│   │   ├── prompt_templates/
│   │   ├── messages/
│   │   ├── function_calls/
│   │   ├── error_logs/
│   │   └── system_config/
├── views.py
├── urls.py
└── README.md
```

## Views and URLs

The admin UI provides views for:

- **Dashboard**: Overview of the system
- **Message Sources**: Configure and manage message sources
- **API Connections**: Configure and manage API connections
- **Prompt Templates**: Configure and manage OpenAI prompt templates
- **Messages**: View and manage messages
- **Function Calls**: View and manage function calls
- **Error Logs**: View and manage error logs
- **System Config**: Configure system settings

## Customization

The UI is designed to be easily customizable:

- **Tailwind Config**: Customize colors, fonts, and other design tokens
- **Custom CSS**: Add custom styles in `static/admin_ui/css/custom.css`
- **JavaScript**: Add custom JavaScript in `static/admin_ui/js/main.js`
- **Templates**: Customize templates in the `templates/admin_ui/` directory

## Development

To work on the UI:

1. Install dependencies: `pip install -r requirements.txt`
2. Install Tailwind CSS dependencies: `cd theme/static_src && npm install`
3. Run Tailwind in development mode: `npm run dev`
4. Run the Django development server: `python manage.py runserver`

## Credits

- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)
- [HTMX](https://htmx.org/)
- [Inter Font](https://rsms.me/inter/)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [Heroicons](https://heroicons.com/)
