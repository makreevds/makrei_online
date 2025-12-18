# Generated manually

from django.db import migrations


def create_initial_cryptocurrencies(apps, schema_editor):
    """Создаёт начальные криптовалюты."""
    Cryptocurrency = apps.get_model('wallet', 'Cryptocurrency')
    
    cryptocurrencies = [
        {
            'name': 'Bitcoin',
            'symbol': 'BTC',
            'network': 'Bitcoin',
            'decimals': 8,
            'is_active': True,
        },
        {
            'name': 'Ethereum',
            'symbol': 'ETH',
            'network': 'Ethereum',
            'decimals': 18,
            'is_active': True,
        },
    ]
    
    for crypto_data in cryptocurrencies:
        Cryptocurrency.objects.get_or_create(
            symbol=crypto_data['symbol'],
            defaults=crypto_data
        )


def reverse_initial_cryptocurrencies(apps, schema_editor):
    """Удаляет начальные криптовалюты."""
    Cryptocurrency = apps.get_model('wallet', 'Cryptocurrency')
    Cryptocurrency.objects.filter(symbol__in=['BTC', 'ETH']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_cryptocurrencies,
            reverse_initial_cryptocurrencies
        ),
    ]

