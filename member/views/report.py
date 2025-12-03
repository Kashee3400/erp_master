from all_imports import *
from erp_app.models import Mpp
from facilitator.models.facilitator_model import AssignedMppToFacilitator
from erp_app.models import BusinessHierarchySnapshot
from collections import defaultdict, Counter


class AppInstalledData(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        mode = request.GET.get("mode", "with")  # "with" or "without"

        # Filters
        mcc_code = request.GET.get("mcc_code")
        mpp_codes_param = request.GET.get("mpp_codes")

        # Date range for WITH mode
        from_date = request.GET.get("from")
        to_date = request.GET.get("to")

        mpp_codes = (
            [code.strip() for code in mpp_codes_param.split(",")]
            if mpp_codes_param
            else None
        )

        # -----------------------------------------------------
        # COMMON SECTION (used in both modes)
        # -----------------------------------------------------

        # Build facilitator lookup
        facilitator_lookup = {
            row[
                "mpp_code"
            ]: f"{row['sahayak__first_name']} {row['sahayak__last_name']}".strip()
            for row in AssignedMppToFacilitator.objects.select_related("sahayak")
            .only("mpp_code", "sahayak__first_name", "sahayak__last_name")
            .values("mpp_code", "sahayak__first_name", "sahayak__last_name")
        }

        # Get all installed users
        user_device_usernames = set(
            UserDevice.objects.filter(Q(module=None) | Q(module="member")).values_list(
                "user__username", flat=True
            )
        )

        # Build Mpp lookup
        mpp_map = {
            mpp.mpp_code: {
                "mpp_code": mpp.mpp_code,
                "name": mpp.mpp_name,
                "mpp_ex_code": mpp.mpp_ex_code,
            }
            for mpp in Mpp.objects.all()
        }

        # Build Mcc lookup
        mcc_map = {
            mcc.mcc_code: {
                "mcc_code": mcc.mcc_code,
                "name": mcc.mcc_name,
                "mcc_ex_code": mcc.mcc_ex_code,
            }
            for mcc in Mcc.objects.all()
        }

        # Get members based on filters
        members_qs = MemberHierarchyView.objects.filter(is_active=True, is_default=True)

        if mcc_code:
            members_qs = members_qs.filter(mcc_code=mcc_code)
        if mpp_codes:
            members_qs = members_qs.filter(mpp_code__in=mpp_codes)

        members_qs = members_qs.values(
            "mpp_code", "mcc_code", "member_code", "mobile_no"
        )

        # Build MPP data map - EXACT SAME STRUCTURE AS WORKING CODE
        mpp_data_map = defaultdict(
            lambda: {
                "mpp_name": "",
                "mpp_ex_code": "",
                "mpp_code": "",
                "mcc_code": "",
                "mcc_ex_code": "",
                "mcc_name": "",
                "member_codes": [],
                "mobile_numbers": [],
            }
        )

        for m in members_qs:
            mpp_code = m["mpp_code"]
            mcc_code = m["mcc_code"]
            mpp_info = mpp_map.get(mpp_code)
            mcc_info = mcc_map.get(mcc_code)

            if not mpp_info:
                continue  # Skip MPP if not found

            data = mpp_data_map[mpp_code]
            data["mpp_name"] = mpp_info["name"]
            data["mpp_ex_code"] = mpp_info["mpp_ex_code"]
            data["mcc_code"] = mcc_info["mcc_code"] if mcc_info else ""
            data["mcc_name"] = mcc_info["name"] if mcc_info else ""
            data["mcc_ex_code"] = mcc_info["mcc_ex_code"] if mcc_info else ""
            data["member_codes"].append(m["member_code"])
            data["mobile_numbers"].append(m["mobile_no"])

        # -----------------------------------------------------
        # MODE: WITHOUT COLLECTION
        # -----------------------------------------------------
        if mode == "without":
            result = []
            total_members_all = 0
            installed_count_all = 0

            for mpp_code, data in mpp_data_map.items():
                member_codes = data["member_codes"]
                mobile_numbers = data["mobile_numbers"]

                # EXACT SAME LOGIC AS WORKING CODE
                installed_count = sum(
                    1 for m in mobile_numbers if m in user_device_usernames
                )
                total_members = len(member_codes)
                installed_percentage = (
                    (installed_count / total_members * 100) if total_members else 0
                )

                result.append(
                    {
                        "mpp": {
                            "mpp_code": mpp_code,
                            "mpp_ex_code": data["mpp_ex_code"],
                            "name": data["mpp_name"],
                        },
                        "mcc": {
                            "mcc_code": data["mcc_code"],
                            "mcc_ex_code": data["mcc_ex_code"],
                            "name": data["mcc_name"],
                        },
                        "fs_name": facilitator_lookup.get(mpp_code, "NA"),
                        "total_members": total_members,
                        "installed": installed_count,
                        "installed_percentage": round(installed_percentage, 2),
                    }
                )

                total_members_all += total_members
                installed_count_all += installed_count

            grand_total_percentage = (
                (installed_count_all / total_members_all * 100)
                if total_members_all
                else 0
            )

            result.append(
                {
                    "mcc": {"name": "Grand Total"},
                    "total_members": total_members_all,
                    "installed": installed_count_all,
                    "installed_percentage": round(grand_total_percentage, 2),
                    "is_total": True,
                }
            )

            return Response(result, status=status.HTTP_200_OK)

        # -----------------------------------------------------
        # MODE: WITH COLLECTION - EXACT WORKING CODE LOGIC
        # -----------------------------------------------------

        if not (from_date and to_date):
            return Response(
                {"error": "from and to dates are required when mode=with"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
            end_date = make_aware(datetime.strptime(to_date, "%Y-%m-%d")) + timedelta(
                hours=23, minutes=59, seconds=59
            )
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get all member codes
        all_member_codes = [
            code for data in mpp_data_map.values() for code in data["member_codes"]
        ]

        # Get collections in date range
        collections_qs = MppCollection.objects.filter(
            collection_date__range=(start_date, end_date),
            member_code__in=all_member_codes,
        )

        # Count distinct pouring days per member - EXACT SAME AS WORKING CODE
        pourer_counts = (
            collections_qs.annotate(date=TruncDate("collection_date"))
            .values("member_code", "date")
            .distinct()
        )

        pourer_by_member = Counter([item["member_code"] for item in pourer_counts])

        result = []
        total_members_all = 0
        installed_count_all = 0
        total_pourers_all = 0

        for mpp_code, data in mpp_data_map.items():
            member_codes = data["member_codes"]
            mobile_numbers = data["mobile_numbers"]

            # EXACT SAME LOGIC AS WORKING CODE
            installed_count = sum(
                1 for m in mobile_numbers if m in user_device_usernames
            )

            installed_count = sum(
                1 for m in mobile_numbers if m in user_device_usernames
            )

            total_members = len(member_codes)
            installed_percentage = (
                (installed_count / total_members * 100) if total_members else 0
            )
            no_of_pourers = len(
                [code for code in member_codes if code in pourer_by_member]
            )

            result.append(
                {
                    "mpp": {
                        "mpp_code": mpp_code,
                        "mpp_ex_code": data["mpp_ex_code"],
                        "name": data["mpp_name"],
                    },
                    "mcc": {
                        "mcc_code": data["mcc_code"],
                        "mcc_ex_code": data["mcc_ex_code"],
                        "name": data["mcc_name"],
                    },
                    "fs_name": facilitator_lookup.get(mpp_code, "NA"),
                    "total_members": total_members,
                    "pourers": no_of_pourers,
                    "installed": installed_count,
                    "installed_percentage": round(installed_percentage, 2),
                }
            )

            total_members_all += total_members
            installed_count_all += installed_count
            total_pourers_all += no_of_pourers

        grand_total_percentage = (
            (installed_count_all / total_members_all * 100) if total_members_all else 0
        )

        result.append(
            {
                "mcc": {"name": "Grand Total"},
                "mpp": None,
                "total_members": total_members_all,
                "pourers": total_pourers_all,
                "installed": installed_count_all,
                "installed_percentage": round(grand_total_percentage, 2),
                "is_total": True,
            }
        )

        return Response(result, status=status.HTTP_200_OK)


class SahayakAppInstalledData(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Build installed flag lookup (Yes/No) for each mpp_code
        # Step 1: Get all sahayak mpp_codes (with or without device)
        all_mpp_codes = set(Mpp.objects.all().values_list("mpp_ex_code", flat=True))

        installed_mpp_codes = set(
            UserDevice.objects.filter(
                module="sahayak", device__isnull=False
            ).values_list("mpp_code", flat=True)
        )
        # Step 3: Build the lookup
        mpp_codes_lookup = {
            mpp_code: "Yes" if mpp_code in installed_mpp_codes else "No"
            for mpp_code in all_mpp_codes
        }

        # All relevant mpp_codes with installed devices
        mpp_ex_codes = list(mpp_codes_lookup.keys())

        # Build Mpp lookup
        mpp_map = {
            mpp.mpp_ex_code: {
                "mpp_code": mpp.mpp_code,
                "name": mpp.mpp_name,
                "mpp_ex_code": mpp.mpp_ex_code,
            }
            for mpp in Mpp.objects.filter(mpp_ex_code__in=mpp_ex_codes)
        }

        # Facilitator name by mpp_code
        facilitator_lookup = {
            row[
                "mpp_code"
            ]: f"{row['sahayak__first_name']} {row['sahayak__last_name']}".strip()
            for row in AssignedMppToFacilitator.objects.select_related("sahayak")
            .filter(mpp_ex_code__in=mpp_ex_codes)
            .values("mpp_code", "sahayak__first_name", "sahayak__last_name")
        }

        # MCC lookup
        mcc_map = {
            mcc.mcc_code: {
                "mcc_code": mcc.mcc_code,
                "name": mcc.mcc_name,
                "mcc_ex_code": mcc.mcc_ex_code,
            }
            for mcc in Mcc.objects.all()
        }

        # Map each mpp_code to its mcc_code from active/default members
        mcc_lookup = {
            row["mpp_code"]: row["mcc_code"]
            for row in BusinessHierarchySnapshot.objects.all().values(
                "mpp_code", "mcc_code"
            )
        }

        result = []
        for mpp_code in mpp_ex_codes:
            mpp_data = mpp_map.get(mpp_code, {})
            mcc_code = mcc_lookup.get(mpp_data.get("mpp_code"))
            mcc_data = mcc_map.get(mcc_code, {})
            result.append(
                {
                    "mcc_code": mcc_code or "NA",
                    "mcc_name": mcc_data.get("name", "NA"),
                    "mcc_ex_code": mcc_data.get("mcc_ex_code", "NA"),
                    "mpp_code": mpp_code,
                    "mpp_name": mpp_data.get("name", "NA"),
                    "mpp_ex_code": mpp_data.get("mpp_ex_code", "NA"),
                    "fs_name": facilitator_lookup.get(mpp_data.get("mpp_code"), "NA"),
                    "installed": mpp_codes_lookup.get(mpp_code, "No"),
                }
            )

        return Response(result, status=status.HTTP_200_OK)


class FacilitatorAppInstalled(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        # ---------------------------------------------
        # 1. Facilitators who have installed the app
        # ---------------------------------------------
        devices = UserDevice.objects.filter(module="facilitator").select_related("user")

        facilitator_ids = [d.user_id for d in devices]

        # Map UserDevice -> installed facilitators
        device_map = {d.user_id: d for d in devices}

        # ---------------------------------------------
        # 2. Load facilitator → MPP assignments
        # ---------------------------------------------
        assignments = AssignedMppToFacilitator.objects.filter(
            sahayak_id__in=facilitator_ids
        ).values("sahayak_id", "mpp_code")

        # group MPPs per facilitator
        mpp_group = {}
        for a in assignments:
            fid = a["sahayak_id"]
            mpp_group.setdefault(fid, []).append(a["mpp_code"])

        # ---------------------------------------------
        # 3. Load hierarchy for all relevant MPPs
        # ---------------------------------------------
        all_mpp_codes = {a["mpp_code"] for a in assignments}

        hierarchy_map = {
            h.mpp_code: h
            for h in BusinessHierarchySnapshot.objects.filter(
                mpp_code__in=all_mpp_codes, is_default=True
            )
        }

        result = []

        # ---------------------------------------------
        # 4. Build final result row per facilitator
        # ---------------------------------------------
        for fid, device in device_map.items():

            user = device.user
            mpps = mpp_group.get(fid, [])

            # collect details
            mpp_names = []
            mpp_ex_codes = []
            mcc_names = set()
            mcc_ex_codes = set()

            for mpp_code in mpps:
                h = hierarchy_map.get(mpp_code)
                if not h:
                    continue

                mpp_names.append(h.mpp_name)
                mpp_ex_codes.append(h.mpp_ex_code)

                mcc_names.add(h.mcc_name)
                mcc_ex_codes.add(h.mcc_tr_code)

            result.append(
                {
                    "username": user.username,
                    "facilitator": f"{user.first_name} {user.last_name}".strip(),
                    "mcc_name": ", ".join(mcc_names) if mcc_names else "",
                    "mcc_ex_code": ", ".join(mcc_ex_codes) if mcc_ex_codes else "",
                    "mpp_names": ", ".join(mpp_names),
                    "mpp_ex_codes": ", ".join(mpp_ex_codes),
                    "installed": 1,
                    "installed_percentage": 100,
                }
            )

        return Response(result)
