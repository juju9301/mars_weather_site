from django import forms
from django.core.exceptions import ValidationError

from .models import Weather


PLOT_METRIC_CHOICES = (
    ("ls", "Solar longitude"),
    ("max_temp", "Maximum air temperature"),
    ("min_temp", "Minimum air temperature"),
    ("max_gts_temp", "Maximum ground temperature"),
    ("min_gts_temp", "Coldest burst mean"),
    ("pressure", "Pressure"),
    ("sunrise", "Sunrise"),
    ("sunset", "Sunset"),
)


class PlotForm(forms.Form):
    sol_from = forms.IntegerField(
        label="Sol from",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": 1}),
    )
    sol_to = forms.IntegerField(
        label="Sol to",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": 1}),
    )
    metric = forms.ChoiceField(
        label="Metric",
        choices=PLOT_METRIC_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, min_sol=None, max_sol=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_sol = min_sol
        self.max_sol = max_sol

        if min_sol is not None and max_sol is not None:
            for field_name in ("sol_from", "sol_to"):
                self.fields[field_name].widget.attrs.update(
                    {"min": min_sol, "max": max_sol}
                )

    def clean_sol_from(self):
        return self._validate_sol("sol_from")

    def clean_sol_to(self):
        return self._validate_sol("sol_to")

    def _validate_sol(self, field_name):
        sol = self.cleaned_data[field_name]
        if self.min_sol is None or self.max_sol is None:
            raise ValidationError("No weather observations are currently available.")
        if not self.min_sol <= sol <= self.max_sol:
            raise ValidationError(
                f"Enter a sol between {self.min_sol} and {self.max_sol}."
            )
        return sol

    def clean(self):
        cleaned_data = super().clean()
        sol_from = cleaned_data.get("sol_from")
        sol_to = cleaned_data.get("sol_to")

        if sol_from is None or sol_to is None:
            return cleaned_data
        if sol_from >= sol_to:
            self.add_error("sol_to", "Sol to must be greater than Sol from.")
            return cleaned_data

        available_endpoints = set(
            Weather.objects.filter(sol__in=(sol_from, sol_to)).values_list(
                "sol", flat=True
            )
        )
        for field_name, sol in (("sol_from", sol_from), ("sol_to", sol_to)):
            if sol not in available_endpoints:
                self.add_error(
                    field_name,
                    f"Sol {sol} is not present in the weather database.",
                )

        return cleaned_data
