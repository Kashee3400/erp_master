# forms.py

from django import forms
from .models import *
from erp_app.models import Product,Brand,ProductCategory, Warehouse, BinLocation,Mcc,Mpp
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, ButtonHolder
from django import forms
from .models import SahayakIncentives

from django import forms
from .models import SahayakIncentives
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column

class SahayakIncentivesForm(forms.ModelForm):
    class Meta:
        model = SahayakIncentives
        fields = ['user', 'mcc_code', 'mcc_name', 'mpp_code', 'mpp_name', 'month', 'opening', 'milk_incentive', 'other_incentive', 'payable', 'closing']

    def __init__(self, *args, **kwargs):
        super(SahayakIncentivesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Fieldset(
                'Incentive Details',
                Row(
                    Column('user', css_class='form-group col-md-4 mb-0'),
                    Column('mcc_code', css_class='form-group col-md-4 mb-0'),
                    Column('mcc_name', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('mpp_code', css_class='form-group col-md-4 mb-0'),
                    Column('mpp_name', css_class='form-group col-md-4 mb-0'),
                    Column('month', css_class='form-group col-md-4 mb-0'),
                ),
            ),
            Fieldset(
                'Financials',
                Row(
                    Column('opening', css_class='form-group col-md-4 mb-0'),
                    Column('milk_incentive', css_class='form-group col-md-4 mb-0'),
                    Column('other_incentive', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('payable', css_class='form-group col-md-4 mb-0'),
                    Column('closing', css_class='form-group col-md-4 mb-0'),
                ),
            )
        )


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Select Excel File',
        help_text='Upload a .xlsx file to import data'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith('.xlsx'):
            raise forms.ValidationError('Only .xlsx files are allowed!')
        return file

class DataFilterForm(forms.Form):
    mpp_code = forms.ModelMultipleChoiceField(
        queryset=Mpp.objects.all(),
        required=False,
        to_field_name='mpp_code',
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select select2",  # Add 'select2' class for JS
                "data-placeholder": "Select MPP Code",
            }
        )
    )

    mcc_code = forms.ModelChoiceField(
        queryset=Mcc.objects.all(),
        required=False,
        to_field_name='mcc_code',
        empty_label="Select MCC Code",
        widget=forms.Select(
            attrs={
                "class": "form-select select2",  # Add 'select2' class for JS
            }
        )
    )
