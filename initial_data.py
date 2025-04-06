#!/usr/bin/env python
"""
Script to create initial data for the API Hub application.
Run this after migrations to set up initial data.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_hub.settings')
django.setup()

from openai_processor.models import PromptTemplate
from message_receiver.models import MessageSource
from api_connector.models import APIAuthentication, APIConfiguration, APIEndpoint, FunctionDefinition

def create_prompt_templates():
    """Create initial prompt templates"""
    
    # Sentry error prompt template
    sentry_template, created = PromptTemplate.objects.get_or_create(
        name="Default Sentry Template",
        defaults={
            'description': "Template for processing Sentry error messages",
            'system_prompt': """
You are an AI assistant that analyzes error reports from Sentry and determines their severity and appropriate actions.
Your task is to analyze the error details and decide if it should be logged as a bug in Linear.

When analyzing errors, consider:
1. The error type and message
2. The stack trace
3. The frequency and recency of the error
4. The impact on users

Based on your analysis, you should call the appropriate function to log the error in Linear if needed.
""",
            'user_prompt_template': """
Please analyze the following error from Sentry:

Error Details:
{{message}}

Source: {{source}}
External ID: {{external_id}}
Received at: {{received_at}}

If this error requires immediate attention, please call the create_linear_issue function with appropriate severity.
Severity levels:
- Urgent: Critical errors affecting many users or core functionality
- High: Serious errors affecting some users or important functionality
- Medium: Errors affecting a small number of users or non-critical functionality
- Low: Minor errors with minimal user impact

If the error is a duplicate or not worth tracking, you can ignore it.
""",
            'model': 'gpt-4o',
            'temperature': 0.3,
            'max_tokens': 1000,
            'function_calling_enabled': True
        }
    )
    print(f"Sentry template {'created' if created else 'already exists'}")
    
    # WhatsApp message prompt template
    whatsapp_template, created = PromptTemplate.objects.get_or_create(
        name="Default WhatsApp Template",
        defaults={
            'description': "Template for processing WhatsApp messages",
            'system_prompt': """
You are an AI assistant that analyzes messages from a WhatsApp group and determines if they contain feature requests, bug reports, or other actionable items.
Your task is to analyze the message content and decide if it should be logged in Linear.

When analyzing messages, consider:
1. Is this a feature request? If so, what is being requested?
2. Is this a bug report? If so, what is the issue?
3. Is this feedback that should be tracked?
4. Is this just conversation that can be ignored?

Based on your analysis, you should call the appropriate function to log the item in Linear if needed.
""",
            'user_prompt_template': """
Please analyze the following message from WhatsApp:

Message:
{{message}}

Source: {{source}}
External ID: {{external_id}}
Received at: {{received_at}}

If this message contains a feature request, bug report, or important feedback, please call the create_linear_issue function with appropriate details.
Issue types:
- Bug: Reports of something not working correctly
- Feature: Requests for new functionality
- Improvement: Suggestions to enhance existing functionality
- Feedback: General feedback that should be tracked

If the message is just conversation or not worth tracking, you can ignore it.
""",
            'model': 'gpt-4o',
            'temperature': 0.5,
            'max_tokens': 1000,
            'function_calling_enabled': True
        }
    )
    print(f"WhatsApp template {'created' if created else 'already exists'}")

def create_message_sources():
    """Create initial message sources"""
    
    # Sentry webhook source
    sentry_source, created = MessageSource.objects.get_or_create(
        name="Sentry Error Webhook",
        defaults={
            'source_type': 'sentry',
            'description': "Webhook for receiving Sentry error reports",
            'webhook_url_path': 'sentry-webhook',
            'webhook_secret': 'your-webhook-secret-here',
            'config': {
                'external_id_path': 'event_id',
                'prompt_template_name': 'Default Sentry Template'
            },
            'is_active': True
        }
    )
    print(f"Sentry source {'created' if created else 'already exists'}")
    
    # WhatsApp webhook source
    whatsapp_source, created = MessageSource.objects.get_or_create(
        name="WhatsApp Webhook",
        defaults={
            'source_type': 'whatsapp',
            'description': "Webhook for receiving WhatsApp messages",
            'webhook_url_path': 'whatsapp-webhook',
            'webhook_secret': 'your-webhook-secret-here',
            'config': {
                'prompt_template_name': 'Default WhatsApp Template'
            },
            'is_active': True
        }
    )
    print(f"WhatsApp source {'created' if created else 'already exists'}")

def create_linear_api_config():
    """Create Linear API configuration"""
    
    # Linear API authentication
    linear_auth, created = APIAuthentication.objects.get_or_create(
        name="Linear API Key",
        defaults={
            'auth_type': 'api_key',
            'api_key': 'your-linear-api-key-here',
            'api_key_name': 'Authorization',
        }
    )
    print(f"Linear auth {'created' if created else 'already exists'}")
    
    # Linear API configuration
    linear_config, created = APIConfiguration.objects.get_or_create(
        name="Linear API",
        defaults={
            'description': "Linear API for issue tracking",
            'base_url': 'https://api.linear.app',
            'authentication': linear_auth,
            'rate_limit_enabled': True,
            'rate_limit': '100/minute',
            'max_retries': 3,
            'retry_backoff': True,
            'default_headers': {
                'Content-Type': 'application/json'
            },
            'is_active': True
        }
    )
    print(f"Linear config {'created' if created else 'already exists'}")
    
    # Create issue endpoint
    create_issue_endpoint, created = APIEndpoint.objects.get_or_create(
        api_config=linear_config,
        name="Create Issue",
        defaults={
            'description': "Create a new issue in Linear",
            'path': 'graphql',
            'http_method': 'POST',
            'request_body_template': {
                'query': '''
                mutation CreateIssue($title: String!, $description: String, $teamId: String!, $priority: Int, $labelIds: [String!]) {
                  issueCreate(input: {
                    title: $title,
                    description: $description,
                    teamId: $teamId,
                    priority: $priority,
                    labelIds: $labelIds
                  }) {
                    success
                    issue {
                      id
                      identifier
                      url
                    }
                  }
                }
                ''',
                'variables': {
                    'title': '',
                    'description': '',
                    'teamId': '',
                    'priority': 0,
                    'labelIds': []
                }
            },
            'is_active': True
        }
    )
    print(f"Create issue endpoint {'created' if created else 'already exists'}")
    
    # Create function definition for OpenAI
    create_issue_function, created = FunctionDefinition.objects.get_or_create(
        name="create_linear_issue",
        defaults={
            'description': "Create a new issue in Linear",
            'api_endpoint': create_issue_endpoint,
            'parameters_schema': {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue"
                    },
                    "team": {
                        "type": "string",
                        "description": "Team identifier (e.g., ENG for Engineering)",
                        "default": "ENG"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["urgent", "high", "medium", "low"],
                        "description": "Priority of the issue"
                    },
                    "labels": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Labels to apply to the issue"
                    }
                },
                "required": ["title", "description", "priority"]
            },
            'parameter_mapping': {
                'variables.title': 'title',
                'variables.description': 'description',
                'variables.teamId': {
                    'transform': 'map',
                    'field': 'team',
                    'mapping': {
                        'ENG': 'team-eng-id-here',
                        'PRODUCT': 'team-product-id-here',
                        'DESIGN': 'team-design-id-here'
                    },
                    'default': 'team-eng-id-here'
                },
                'variables.priority': {
                    'transform': 'map',
                    'field': 'priority',
                    'mapping': {
                        'urgent': 1,
                        'high': 2,
                        'medium': 3,
                        'low': 4
                    },
                    'default': 3
                },
                'variables.labelIds': 'labels'
            },
            'is_active': True
        }
    )
    print(f"Create issue function {'created' if created else 'already exists'}")

def main():
    """Main function to create all initial data"""
    print("Creating initial data...")
    create_prompt_templates()
    create_message_sources()
    create_linear_api_config()
    print("Initial data creation complete!")

if __name__ == "__main__":
    main()
