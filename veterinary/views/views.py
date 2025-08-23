# from rest_framework import generics, status
# from rest_framework.views import APIView
# from django.core.files.storage import default_storage
# from rest_framework.response import Response
# from ..serializers import *
# from ..models.models import *
# from ..models.camp_models import *
# from ..models.case_models import *
# from ..models.stock_models import *
# from rest_framework.permissions import AllowAny,IsAdminUser,IsAuthenticated
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from django.core.exceptions import ObjectDoesNotExist
# from rest_framework.exceptions import PermissionDenied, ValidationError



# class CattleCaseTypeViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = CattleCaseType.objects.all()
#     serializer_class = CattleCaseTypeSerializer


# class TimeSlotViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = TimeSlot.objects.all()
#     serializer_class = TimeSlotSerializer

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "time_slots": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "time_slots": []
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "time_slot": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response = {
#                 "status": status.HTTP_201_CREATED,
#                 "message": "Created",
#                 "time_slot": serializer.data
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Updated",
#                 "time_slot": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response = {
#                 "status": status.HTTP_204_NO_CONTENT,
#                 "message": "Deleted",
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_204_NO_CONTENT)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "time_slot": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class PaymentMethodViewSet(viewsets.ModelViewSet):
    
#     permission_classes = [AllowAny]
#     queryset = PaymentMethod.objects.all()
#     serializer_class = PaymentMethodSerializer

#     def format_response(self, status_code, message, data):
#         return {
#             "status": status_code,
#             "message": message,
#             "payment_methods": data
#         }

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response_data = self.format_response(status.HTTP_200_OK, "Success", serializer.data)
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             response_data = self.format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e), [])
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response_data = self.format_response(status.HTTP_200_OK, "Success", serializer.data)
#             return Response(response_data, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response_data = self.format_response(status.HTTP_404_NOT_FOUND, "Not Found", {})
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response_data = self.format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e), {})
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response_data = self.format_response(status.HTTP_201_CREATED, "Created", serializer.data)
#             return Response(response_data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             response_data = self.format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e), {})
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response_data = self.format_response(status.HTTP_200_OK, "Updated", serializer.data)
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Exception as e:
#             response_data = self.format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e), {})
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response_data = self.format_response(status.HTTP_204_NO_CONTENT, "Deleted", {})
#             return Response(response_data, status=status.HTTP_204_NO_CONTENT)
#         except Exception as e:
#             response_data = self.format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e), {})
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class DiagnosisRouteViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = DiagnosisRoute.objects.all()
#     serializer_class = DiagnosisRouteSerializer


#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "diagnose_route": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "data": []
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "diagnose_route": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response = {
#                 "status": status.HTTP_201_CREATED,
#                 "message": "Created",
#                 "diagnose_route": serializer.data
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Updated",
#                 "diagnose_route": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response = {
#                 "status": status.HTTP_204_NO_CONTENT,
#                 "message": "Deleted",
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_204_NO_CONTENT)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "diagnose_route": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class SymptomsViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = Symptoms.objects.all()
#     serializer_class = SymptomsSerializer

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "symptoms": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "symptoms": []
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "symptom": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response = {
#                 "status": status.HTTP_201_CREATED,
#                 "message": "Created",
#                 "symptom": serializer.data
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Updated",
#                 "symptom": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response = {
#                 "status": status.HTTP_204_NO_CONTENT,
#                 "message": "Deleted",
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_204_NO_CONTENT)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "symptom": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class DiseaseViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = Disease.objects.all()
#     serializer_class = DiseaseSerializer

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "disease": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "disease": []
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "disease": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response = {
#                 "status": status.HTTP_201_CREATED,
#                 "message": "Created",
#                 "disease": serializer.data
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Updated",
#                 "disease": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response = {
#                 "status": status.HTTP_204_NO_CONTENT,
#                 "message": "Deleted",
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_204_NO_CONTENT)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "disease": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CattleTaggingViewSet(viewsets.ModelViewSet):
#     permission_classes = [AllowAny]
#     queryset = CattleTagging.objects.all()
#     serializer_class = CattleTaggingSerializer

#     def list(self, request, *args, **kwargs):
#         try:
#             queryset = self.get_queryset()
#             serializer = self.get_serializer(queryset, many=True)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "cattle_tagging": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "cattle_tagging": []
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             serializer = self.get_serializer(instance)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "cattle_tagging": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             response = {
#                 "status": status.HTTP_201_CREATED,
#                 "message": "Created",
#                 "cattle_tagging": serializer.data
#             }
#             return Response(response, status=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             response = {
#                 "status": status.HTTP_200_OK,
#                 "message": "Updated",
#                 "cattle_tagging": serializer.data
#             }
#             return Response(response, status=status.HTTP_200_OK)
#         except ValidationError as e:
#             response = {
#                 "status": status.HTTP_400_BAD_REQUEST,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_400_BAD_REQUEST)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def destroy(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             response = {
#                 "status": status.HTTP_204_NO_CONTENT,
#                 "message": "Deleted",
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_204_NO_CONTENT)
#         except ObjectDoesNotExist:
#             response = {
#                 "status": status.HTTP_404_NOT_FOUND,
#                 "message": "Not Found",
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             response = {
#                 "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 "message": str(e),
#                 "cattle_tagging": {}
#             }
#             return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CaseEntryViewSet(viewsets.ModelViewSet):
#     queryset = CaseEntry.objects.all()
#     serializer_class = CaseEntrySerializer

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         data = {"success": True, "data": serializer.data}
#         return Response(data)

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance)
#         data = {"success": True, "data": serializer.data}
#         return Response(data)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         data = {"success": True, "data": serializer.data}
#         return Response(data, status=status.HTTP_201_CREATED, headers=headers)

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         data = {"success": True, "data": serializer.data}
#         return Response(data)

#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         data = {"success": True, "message": "Item deleted successfully."}
#         return Response(data, status=status.HTTP_204_NO_CONTENT)
