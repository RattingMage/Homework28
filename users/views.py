import http
import json

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from ads.models import Ad, Category
from users.models import User, Location

PAGE_NUMBER = 4


class UserDetailView(DetailView):
    model = User

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        return JsonResponse({
            "id": user.pk,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role,
            "age": user.age,
            "locations": [loc.name for loc in user.location.all()]
        }, safe=False)


class UserListView(ListView):
    model = User
    queryset = User.objects.annotate(total_ads=Count("ad", filter=Q(ad__is_published=True)))

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        return JsonResponse([{
            "id": user.pk,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role,
            "age": user.age,
            "total_ads": user.total_ads,
            "locations": [loc.name for loc in user.location.all()]
        } for user in self.object_list], safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class UserCreateView(CreateView):
    model = User
    fields = "__all__"

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        new_user = User.objects.create(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("username"),
            role=data.get("role"),
            age=data.get("age"),
        )
        locations = data.get("locations")
        if locations:
            for loc_name in data.get("locations"):
                loc, created = Location.objects.get_or_create(name=loc_name)
                new_user.location.add(loc)

        return JsonResponse({
            "id": new_user.pk,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "username": new_user.username,
            "role": new_user.role,
            "age": new_user.age,
            "locations": [loc.name for loc in new_user.location.all()]
        }, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class UserUpdateView(UpdateView):
    model = User
    fields = "__all__"

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        data = json.loads(request.body)

        if "first_name" in data:
            self.object.first_name = data.get("first_name")
        if "last_name" in data:
            self.object.last_name = data.get("last_name")
        if "username" in data:
            self.object.username = data.get("username")
        if "role" in data:
            self.object.role = data.get("role")
        if "age" in data:
            self.object.age = data.get("age")
        if "locations" in data:
            self.object.location.all().delete()
            for loc_name in data.get("locations"):
                loc, created = Location.objects.get_or_create(name=loc_name)
                self.object.location.add(loc)

        return JsonResponse({
            "id": self.object.pk,
            "first_name": self.object.first_name,
            "last_name": self.object.last_name,
            "username": self.object.username,
            "role": self.object.role,
            "age": self.object.age,
            "locations": [loc.name for loc in self.object.location.all()]
        }, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class UserDeleteView(DeleteView):
    model = User
    success_url = "/"

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        return JsonResponse({"status": "OK"}, status=http.HTTPStatus.NO_CONTENT, safe=False)
