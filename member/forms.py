# forms.py

from django import forms
from .models import *
from erp_app.models import Product,Brand,ProductCategory, Warehouse, BinLocation
from django.utils.translation import gettext_lazy as _


class ProductImageForm(forms.ModelForm):
    product_code = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_saleable=True),
        empty_label=_("Select Product"),
        label=_("Product")
    )

    class Meta:
        model = ProductImage
        fields = ['product_code', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_code'].label_from_instance = lambda obj: obj.product_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_product = self.cleaned_data['product_code']
        instance.product_code = selected_product.product_code
        instance.product_name = selected_product.product_name
        if commit:
            instance.save()
        return instance


class BrandImageForm(forms.ModelForm):
    brand_code = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        empty_label=_("Select Brand"),
        label=_("Brand")
    )

    class Meta:
        model = BrandImage
        fields = ['brand_code', 'image']

    def __init__(self, *args, **kwargs):
        super(BrandImageForm, self).__init__(*args, **kwargs)
        self.fields['brand_code'].label_from_instance = lambda obj: obj.brand_name

    def save(self, commit=True):
        instance = super(BrandImageForm, self).save(commit=False)
        # Retrieve the selected brand object to get the brand_name
        selected_brand = self.cleaned_data['brand_code']
        instance.brand_code = selected_brand.brand_code
        instance.brand_name = selected_brand.brand_name
        if commit:
            instance.save()
        return instance

class CategoryImageForm(forms.ModelForm):
    category_code = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        empty_label=_("Select Product Category"),
        label=_("Product Category")
    )

    class Meta:
        model = CategoryImage
        fields = ['category_code', 'image']

    def __init__(self, *args, **kwargs):
        super(CategoryImageForm, self).__init__(*args, **kwargs)
        self.fields['category_code'].label_from_instance = lambda obj: obj.product_category_name

    def save(self, commit=True):
        instance = super(CategoryImageForm, self).save(commit=False)
        selected_brand = self.cleaned_data['category_code']
        instance.category_code = selected_brand.product_category_code
        instance.category_name = selected_brand.product_category_name
        if commit:
            instance.save()
        return instance

class ProductStockOpeningForm(forms.ModelForm):
    product_code = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_saleable=True),
        empty_label=_("Select Product"),
        label=_("Product")
    )
    warehouse_code = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        empty_label=_("Select Warehouse"),
        label=_("Warehouse")
    )
    bin_location_code = forms.ModelChoiceField(
        queryset=BinLocation.objects.all(),
        empty_label=_("Select Bin Location"),
        label=_("Bin Location")
    )

    class Meta:
        model = ProductStockOpening
        fields = [
            'product_code', 'warehouse_code', 'bin_location_code',
            'qty', 'as_on_date', 'created_by',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product_code'].label_from_instance = lambda obj: obj.product_name
        self.fields['warehouse_code'].label_from_instance = lambda obj: obj.warehouse_name
        self.fields['bin_location_code'].label_from_instance = lambda obj: obj.bin_location_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_product = self.cleaned_data['product_code']
        selected_warehouse = self.cleaned_data['warehouse_code']
        selected_bin_location = self.cleaned_data['bin_location_code']
        instance.product_code = selected_product.product_code
        instance.product_name = selected_product.product_name
        instance.warehouse_code = int(selected_warehouse.warehouse_code) 
        instance.warehouse_name = selected_warehouse.warehouse_name
        instance.bin_location_code = int(selected_bin_location.bin_location_code)  # Ensure the code is an integer
        instance.bin_location_name = selected_bin_location.bin_location_name
        
        if commit:
            instance.save()
        return instance


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()