# Django API Hub - Tailwind CSS Theme

This app provides the Tailwind CSS theme for the Django API Hub.

## Setup

The theme app is already configured in the project settings. To use it:

1. Install the required dependencies:

```bash
pip install django-tailwind django-browser-reload
```

2. Install the Node.js dependencies:

```bash
cd theme/static_src
npm install
```

## Development

To work on the theme in development mode:

```bash
cd theme/static_src
npm run dev
```

This will start the Tailwind CSS compiler in watch mode, which will automatically rebuild the CSS when you make changes to the source files.

## Production

To build the theme for production:

```bash
cd theme/static_src
npm run build
```

This will create a minified CSS file in `static/css/dist/styles.css`.

## Customization

### Tailwind Configuration

You can customize the Tailwind CSS configuration in `theme/static_src/tailwind.config.js`. This file contains the theme settings, such as colors, fonts, and other design tokens.

### Custom CSS

You can add custom CSS in `theme/static_src/src/styles/index.css`. This file is processed by PostCSS and includes the Tailwind CSS directives.

### Templates

The theme app doesn't include any templates. Templates are provided by the `admin_ui` app.

## Structure

```
theme/
├── static_src/
│   ├── src/
│   │   └── styles/
│   │       └── index.css
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
├── templates/
├── __init__.py
├── apps.py
└── README.md
```

## Credits

- [Tailwind CSS](https://tailwindcss.com/)
- [django-tailwind](https://github.com/timonweb/django-tailwind)
- [django-browser-reload](https://github.com/adamchainz/django-browser-reload)
