from django import forms
from .models import AssignedMppToFacilitator
from erp_app.models import Mpp


class AssignedMppToFacilitatorForm(forms.ModelForm):
    mpp = forms.ModelChoiceField(
        queryset=Mpp.objects.all(),
        label="Select MPP",
        required=True,
    )

    class Meta:
        model = AssignedMppToFacilitator
        fields = ["sahayak"]

    def save(self, commit=True):
        # Get the selected MPP
        selected_mpp = self.cleaned_data['mpp']
        # Set the fields on the instance
        self.instance.mpp_code = selected_mpp.mpp_code
        self.instance.mpp_ex_code = selected_mpp.mpp_ex_code
        self.instance.mpp_name = selected_mpp.mpp_name
        self.instance.mpp_short_name = selected_mpp.mpp_short_name
        self.instance.mpp_type = selected_mpp.mpp_type
        self.instance.mpp_logo = selected_mpp.mpp_logo
        self.instance.mpp_icon = selected_mpp.mpp_icon
        self.instance.mpp_punch_line = selected_mpp.mpp_punch_line
        self.instance.mpp_opening_date = selected_mpp.mpp_opening_date

        # Call the parent save method
        return super().save(commit)
