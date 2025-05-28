from rest_framework import generics, status, viewsets, exceptions, decorators, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser,IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import requests
from member.serialzers import *
from erp_app.models import (
    MemberMaster,
    Mpp,
    LocalSaleTxn,
    MemberHierarchyView,
    BillingMemberDetail,
    MppCollection,
    MppCollectionReferences,
    RmrdMilkCollection,
    PriceBook,
    PriceBookDetail,
    Mcc,
)
from django.core.exceptions import ValidationError
from django.db import DatabaseError,IntegrityError,InterfaceError,InternalError
from erp_app.serializers import (
    MemberHierarchyViewSerializer,
    MccSerializer,
    MppSerializer,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from import_export.admin import ImportExportModelAdmin
from import_export.forms import (
    ImportForm,
)
from django_filters import FilterSet, DateFromToRangeFilter, DateTimeFromToRangeFilter
from member.resources import SahayakIncentivesResource
import csv
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django_filters import rest_framework as filters
import os
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from member.forms import *
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Q
from django.conf import settings
from member.filters import SahayakIncentivesFilter, MemberHeirarchyFilter
from facilitator.authentication import ApiKeyAuthentication
from datetime import date
from django.utils.dateparse import parse_date
from django.db.models import Sum, Count, Avg
from django.utils.timezone import make_aware, now
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from django.db.models import Sum, F, FloatField, DecimalField
from django.db.models.functions import Coalesce, Cast
from django.utils.translation import gettext as _
from django.core.cache import cache
from member.models import UserDevice
import logging

User = get_user_model()
