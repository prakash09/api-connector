# Django API Hub

A flexible Django application that receives messages from various sources, processes them with OpenAI, and calls external APIs based on the processed output.

## Features

- **Message Receiver**: Receive messages from various sources (Sentry, WhatsApp, etc.)
- **OpenAI Processing**: Process messages with OpenAI and use function calling
- **API Connector**: Connect to external APIs with authentication, rate limiting, and retry logic
- **Admin Panel**: Configure APIs, message sources, and prompt templates
- **Webhooks**: Receive webhooks from external services
- **Async Processing**: Process messages asynchronously with Celery
- **Rate Limiting**: Avoid unnecessary API calls with configurable rate limits
- **Retry Logic**: Automatically retry failed API calls with exponential backoff

## Use Cases

1. **Error Tracking**: Receive error reports from Sentry, analyze them with OpenAI, and create issues in Linear
2. **Message Processing**: Receive messages from WhatsApp, analyze them with OpenAI, and create issues or feature requests in Linear
3. **Custom Integrations**: Add your own message sources and API integrations

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Redis (for Celery)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd django_api_hub
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:

```
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key

# OpenAI settings
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o

# Database settings (if using PostgreSQL)
DB_NAME=api_hub
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis settings
REDIS_URL=redis://localhost:6379/0
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Load initial data:

```bash
python initial_data.py
```

7. Run the development server:

```bash
python manage.py runserver
```

8. Start Celery worker (in a separate terminal):

```bash
celery -A api_hub worker -l info
```

## Configuration

### Admin Panel

Access the admin panel at `http://localhost:8000/admin/` to configure:

- **API Configurations**: Configure external APIs with authentication, rate limiting, etc.
- **API Endpoints**: Define API endpoints for each API configuration
- **Function Definitions**: Define functions that can be called by OpenAI
- **Message Sources**: Configure sources for receiving messages
- **Prompt Templates**: Configure templates for OpenAI prompts

### Message Sources

Configure message sources in the admin panel:

- **Webhook-based sources**: Configure webhook URL paths and secrets
- **API-based sources**: Configure API endpoints for receiving messages

### API Configurations

Configure API connections in the admin panel:

- **Authentication**: Configure API keys, tokens, basic auth, or OAuth
- **Rate Limiting**: Configure rate limits for each API
- **Retry Logic**: Configure retry attempts and backoff strategy

### Prompt Templates

Configure OpenAI prompt templates in the admin panel:

- **System Prompt**: Set the context for the OpenAI model
- **User Prompt Template**: Define the template for user prompts with placeholders
- **Model Configuration**: Configure model, temperature, max tokens, etc.
- **Function Calling**: Enable or disable function calling

## API Reference

### Webhook Endpoints

- `POST /webhook/<path>/`: Receive webhooks from external services

### API Endpoints

- `POST /api/messages/`: Send a message for processing
- `GET /api/messages/<message_id>/`: Get the status of a message

## Development

### Project Structure

```
django_api_hub/
├── api_hub/                # Project settings and configuration
├── api_connector/          # API connector app
├── core/                   # Core functionality
├── message_receiver/       # Message receiver app
├── openai_processor/       # OpenAI processor app
├── .env                    # Environment variables
├── initial_data.py         # Initial data script
├── manage.py               # Django management script
└── README.md               # This file
```

### Adding a New Message Source

1. Create a new `MessageSource` in the admin panel
2. Configure the webhook URL path or API endpoint
3. Create a prompt template for the message source
4. Test the integration

### Adding a New API Integration

1. Create a new `APIAuthentication` in the admin panel
2. Create a new `APIConfiguration` with the authentication
3. Create `APIEndpoint`s for the API
4. Create `FunctionDefinition`s for OpenAI function calling
5. Test the integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
