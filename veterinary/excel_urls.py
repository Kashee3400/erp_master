# urls.py
from django.urls import path,include
from .views import excel_import_view as views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"excel-sessions", views.ExcelSessionViewSet, basename="excelsessions")

urlpatterns = [
    path("",include(router.urls)),
    path('import/', views.ExcelImportConfirmView.as_view(), name='excel_import'),
    path('export/', views.ExcelExportView.as_view(), name='excel_export'),
    path('import-model/', views.ImportableModelsView.as_view(), name='import_models'),
    path("sample/<str:target_model>/", views.download_sample_excel, name="download_sample_excel"),
]
