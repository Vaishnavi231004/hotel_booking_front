from django import forms

class ReviewForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5, label="Rating (1-5)")
    comment = forms.CharField(widget=forms.Textarea, required=True, label="Comment")
