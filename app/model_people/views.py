from app.model import views
from . import models

# Create your views here.


class ModelList(views.ListView):
    model = models.Model
    classify = models.Classify


class ModelCreate(views.CreateView):
    model = models.Model


class ModelDetail(views.DetailView):
    field_mode = models.Field
    classify = models.Classify
    model = models.Model


class ModelEdit(views.UpdateView):
    model = models.Model


class ModelDelete(views.DeleteView):
    model = models.Model


class ModelVote(views.VoteView):
    model = models.Model
    vote_model = models.Vote


class ModelClassify(views.ClassifyView):
    field_mode = models.Field
    classify = models.Classify
    model = models.Model


class ModelField(views.FieldView):
    classify = models.Classify
    model = models.Model


class Filter(views.FilterView):
    field_mode = models.Field
    classify = models.Classify
    model = models.Model


class ModelCompareClassify(views.CompareClassify):
    classify = models.Classify
    model = models.Model


class ModelCompareList(views.CompareList):
    classify = models.Classify
    model = models.Model


class ModelCompareDetail(views.CompareDetail):
    review_model = models.Review
    field_mode = models.Field
    classify = models.Classify
    model = models.Model
