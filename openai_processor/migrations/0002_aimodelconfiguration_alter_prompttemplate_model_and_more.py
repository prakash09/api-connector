# Generated by Django 5.2 on 2025-04-06 21:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openai_processor", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIModelConfiguration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "model_type",
                    models.CharField(
                        choices=[
                            ("openai", "OpenAI"),
                            ("azure", "Azure OpenAI"),
                            ("anthropic", "Anthropic"),
                            ("custom", "Custom OpenAI-compatible"),
                        ],
                        default="openai",
                        max_length=20,
                        verbose_name="Model Type",
                    ),
                ),
                (
                    "base_url",
                    models.URLField(
                        blank=True,
                        help_text="Base URL for the API (leave empty for default OpenAI URL)",
                        verbose_name="Base URL",
                    ),
                ),
                ("api_key", models.CharField(max_length=255, verbose_name="API Key")),
                (
                    "organization_id",
                    models.CharField(
                        blank=True,
                        help_text="OpenAI organization ID (if applicable)",
                        max_length=255,
                        verbose_name="Organization ID",
                    ),
                ),
                (
                    "default_model",
                    models.CharField(
                        default="gpt-4o",
                        help_text="Default model to use (e.g., gpt-4o, claude-3-opus)",
                        max_length=50,
                        verbose_name="Default Model",
                    ),
                ),
                (
                    "default_temperature",
                    models.FloatField(default=0.7, verbose_name="Default Temperature"),
                ),
                (
                    "default_max_tokens",
                    models.PositiveIntegerField(
                        default=1000, verbose_name="Default Max Tokens"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
            ],
            options={
                "verbose_name": "AI Model Configuration",
                "verbose_name_plural": "AI Model Configurations",
            },
        ),
        migrations.AlterField(
            model_name="prompttemplate",
            name="model",
            field=models.CharField(
                default="gpt-4o",
                help_text="Model name (overrides the default model from AI Model Configuration if specified)",
                max_length=50,
                verbose_name="Model",
            ),
        ),
        migrations.AddField(
            model_name="prompttemplate",
            name="ai_model_config",
            field=models.ForeignKey(
                blank=True,
                help_text="AI model configuration to use (leave empty to use system default)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="prompt_templates",
                to="openai_processor.aimodelconfiguration",
                verbose_name="AI Model Configuration",
            ),
        ),
    ]
