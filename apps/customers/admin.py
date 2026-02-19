from django.contrib import admin
from .models import Customer, Pet

class PetInline(admin.TabularInline):
    model = Pet
    extra = 0

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('rut', 'full_name', 'email', 'phone', 'pets_count', 'created_at')
    search_fields = ('rut', 'first_name', 'last_name', 'email')
    list_filter = ('created_at',)
    inlines = [PetInline]

    @admin.display(description='Nombre Completo', ordering='first_name')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description='Mascotas')
    def pets_count(self, obj):
        return obj.pets.count()

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner_link', 'age_years')
    list_filter = ('species', 'age_years')
    search_fields = ('name', 'breed', 'customer__rut', 'customer__first_name')
    
    @admin.display(description='Dueño', ordering='customer')
    def owner_link(self, obj):
        return obj.customer