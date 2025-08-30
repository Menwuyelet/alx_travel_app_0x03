from django.core.management.base import BaseCommand
from listings.models import Listing
import random

class Command(BaseCommand):
    help = 'Seed the database with listings'

    def handle(self, *args, **kwargs):
        sample_locations = ['Addis Ababa', 'Nairobi', 'Lagos', 'Cairo']
        for i in range(10):
            Listing.objects.create(
                title=f"Listing {i+1}",
                description="A cozy place to stay.",
                location=random.choice(sample_locations),
                price_per_night=random.uniform(30.0, 150.0),
                available=bool(random.getrandbits(1))
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded listings'))