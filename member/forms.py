# forms.py

from django import forms
from .models import *
from erp_app.models import Product,Brand,ProductCategory

class ProductImageForm(forms.ModelForm):
    product_code = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_saleable=True),
        empty_label="Select Product",
        label="Product"
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
        empty_label="Select Brand",
        label="Brand"
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
        empty_label="Select Product Category",
        label="Product Category"
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
