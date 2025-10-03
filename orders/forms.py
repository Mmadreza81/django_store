from django import forms

class CardAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10)


class CouponApplyForm(forms.Form):
    code = forms.CharField()

class OrderAddressForm(forms.Form):
    edit_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # آدرس و کد پستی حتمی باید پر شوند اگر آدرس جدید اضافه می‌شود
    address = forms.CharField(max_length=255, required=False)
    postal_code = forms.CharField(max_length=25, required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        edit_id = cleaned_data.get("edit_id")
        address = cleaned_data.get("address")
        postal_code = cleaned_data.get("postal_code")
        if not edit_id and (not address or not postal_code):
            raise forms.ValidationError("برای اضافه کردن آدرس جدید، آدرس و کدپستی لازم است.")
        return cleaned_data
