# Generated by Django 5.2 on 2025-04-06 19:53

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIAuthentication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('auth_type', models.CharField(choices=[('none', 'No Authentication'), ('api_key', 'API Key'), ('bearer', 'Bearer Token'), ('basic', 'Basic Auth'), ('oauth2', 'OAuth 2.0')], max_length=20, verbose_name='Authentication Type')),
                ('api_key', models.CharField(blank=True, max_length=255, null=True, verbose_name='API Key')),
                ('api_key_name', models.CharField(blank=True, help_text='Header name for the API key (e.g., X-API-Key)', max_length=100, null=True, verbose_name='API Key Name')),
                ('token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Token')),
                ('username', models.CharField(blank=True, max_length=100, null=True, verbose_name='Username')),
                ('password', models.CharField(blank=True, max_length=100, null=True, verbose_name='Password')),
                ('client_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Client ID')),
                ('client_secret', models.CharField(blank=True, max_length=255, null=True, verbose_name='Client Secret')),
                ('token_url', models.URLField(blank=True, null=True, verbose_name='Token URL')),
                ('refresh_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Refresh Token')),
                ('access_token', models.CharField(blank=True, max_length=255, null=True, verbose_name='Access Token')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='Expires At')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'API Authentication',
                'verbose_name_plural': 'API Authentications',
            },
        ),
        migrations.CreateModel(
            name='APIConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('base_url', models.URLField(verbose_name='Base URL')),
                ('rate_limit_enabled', models.BooleanField(default=True, verbose_name='Rate Limit Enabled')),
                ('rate_limit', models.CharField(default='100/hour', max_length=50, validators=[django.core.validators.RegexValidator(message='Rate limit must be in format: number/timeunit (e.g., 100/hour)', regex='^\\d+/(?:second|minute|hour|day)$')], verbose_name='Rate Limit')),
                ('max_retries', models.PositiveSmallIntegerField(default=3, verbose_name='Max Retries')),
                ('retry_backoff', models.BooleanField(default=True, help_text='Use exponential backoff for retries', verbose_name='Retry Backoff')),
                ('default_headers', models.JSONField(blank=True, default=dict, verbose_name='Default Headers')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('authentication', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='api_configurations', to='api_connector.apiauthentication')),
            ],
            options={
                'verbose_name': 'API Configuration',
                'verbose_name_plural': 'API Configurations',
            },
        ),
        migrations.CreateModel(
            name='APIEndpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('path', models.CharField(help_text='Relative path from the base URL (e.g., /api/v1/users)', max_length=255, verbose_name='Path')),
                ('http_method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('PATCH', 'PATCH'), ('DELETE', 'DELETE')], default='GET', max_length=10, verbose_name='HTTP Method')),
                ('request_body_template', models.JSONField(blank=True, default=dict, help_text='JSON template for the request body', verbose_name='Request Body Template')),
                ('request_headers', models.JSONField(blank=True, default=dict, verbose_name='Request Headers')),
                ('response_mapping', models.JSONField(blank=True, default=dict, help_text='Mapping of response fields to internal fields', verbose_name='Response Mapping')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('api_config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='endpoints', to='api_connector.apiconfiguration')),
            ],
            options={
                'verbose_name': 'API Endpoint',
                'verbose_name_plural': 'API Endpoints',
                'unique_together': {('api_config', 'name')},
            },
        ),
        migrations.CreateModel(
            name='FunctionDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('parameters_schema', models.JSONField(help_text='JSON Schema for function parameters', verbose_name='Parameters Schema')),
                ('parameter_mapping', models.JSONField(default=dict, help_text='Mapping of function parameters to API request parameters', verbose_name='Parameter Mapping')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('api_endpoint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='function_definitions', to='api_connector.apiendpoint')),
            ],
            options={
                'verbose_name': 'Function Definition',
                'verbose_name_plural': 'Function Definitions',
            },
        ),
    ]
