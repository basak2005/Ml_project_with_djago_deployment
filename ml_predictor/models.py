from django.db import models

# Create your models here.

class PropertyPrediction(models.Model):
    # User information from session
    user_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Numeric Features
    title = models.FloatField(help_text="BHK value")
    price_in_rupees = models.FloatField(help_text="Price per BHK")
    bathroom = models.IntegerField(help_text="Number of bathrooms")
    balcony = models.IntegerField(help_text="Number of balconies")
    super_area = models.FloatField(help_text="Super area in sq ft")
    
    # Categorical Features
    transaction = models.CharField(max_length=50, help_text="Transaction type")
    location = models.CharField(max_length=100, help_text="Property location")
    furnishing = models.CharField(max_length=50, help_text="Furnishing status")
    facing = models.CharField(max_length=50, help_text="Facing direction")
    
    # Text Features
    floor = models.CharField(max_length=100, help_text="Floor details")
    overlooking = models.CharField(max_length=200, help_text="What the property overlooks")
    society = models.CharField(max_length=200, blank=True, null=True, help_text="Society/Building name (optional)")
    
    # Prediction Results
    prediction_xgboost = models.FloatField(null=True, blank=True)
    prediction_decision_tree = models.FloatField(null=True, blank=True)
    prediction_lgbm = models.FloatField(null=True, blank=True)
    prediction_random_forest = models.FloatField(null=True, blank=True)
    prediction_linear_regression = models.FloatField(null=True, blank=True)
    prediction_support_vector = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        user_name = self.user_name if self.user_name else "Anonymous"
        return f"Prediction by {user_name} - {self.location}"
