# Generated by Django 4.2.13 on 2024-07-26 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AreaMaster',
            fields=[
                ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                ('distnm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='DistNm', max_length=50, null=True)),
                ('distcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Distcode', max_length=5, null=True)),
                ('revenuevillagenm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='RevenueVillageNm', max_length=50, null=True)),
                ('revenuevillagecode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Revenuevillagecode', max_length=8, null=True)),
                ('hamletname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='HamletName', max_length=50, null=True)),
                ('hamletcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='HamletCode', max_length=2, null=True)),
                ('mccname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MCCName', max_length=50, null=True)),
                ('mcccode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MCCCode', max_length=10, null=True)),
                ('mppname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MPPName', max_length=50, null=True)),
                ('mppcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MPPcode', max_length=10, null=True)),
                ('statenm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='StateNm', max_length=50, null=True)),
                ('statecode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='StateCode', max_length=5, null=True)),
                ('tehsilnm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='TehsilNm', max_length=50, null=True)),
                ('tehsilcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='TehsilCode', max_length=10, null=True)),
                ('is_active', models.IntegerField(blank=True, db_column='IS_ACTIVE', null=True)),
            ],
            options={
                'db_table': 'Area_Master',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='BankMaster',
            fields=[
                ('bankid', models.AutoField(primary_key=True, serialize=False)),
                ('bankname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='BankName', max_length=50, null=True)),
                ('branchname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='BranchName', max_length=50, null=True)),
                ('ifsccode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='IfscCode', max_length=50, null=True)),
                ('createddt', models.DateTimeField(blank=True, db_column='CreatedDt', null=True)),
                ('updateddt', models.DateTimeField(blank=True, db_column='UpdatedDt', null=True)),
                ('createdby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='CreatedBy', max_length=50, null=True)),
            ],
            options={
                'db_table': 'Bank_Master',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EntryTable',
            fields=[
                ('did', models.AutoField(db_column='Did', primary_key=True, serialize=False)),
                ('formnumber', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FormNumber', max_length=10, null=True)),
                ('applicantnm_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='ApplicantNm_Sec1', max_length=50, null=True)),
                ('fatherhusband_type_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FatherHusband_type_Sec1', max_length=50, null=True)),
                ('fatherhusbandnm_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FatherHusbandNm_Sec1', max_length=50, null=True)),
                ('gender_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Gender_Sec1', max_length=10, null=True)),
                ('age_sec1', models.IntegerField(blank=True, db_column='Age_Sec1', null=True)),
                ('cast_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Cast_Sec1', max_length=20, null=True)),
                ('education_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Education_Sec1', max_length=20, null=True)),
                ('house_number_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='House_Number_Sec1', max_length=50, null=True)),
                ('hamlet_sec1', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Hamlet_Sec1', null=True)),
                ('village_sec1', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Village_Sec1', null=True)),
                ('post_office_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Post_Office_Sec1', max_length=50, null=True)),
                ('tehsil_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Tehsil_Sec1', max_length=50, null=True)),
                ('district_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='District_Sec1', max_length=50, null=True)),
                ('state_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='State_Sec1', max_length=50, null=True)),
                ('pincode_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Pincode_Sec1', max_length=50, null=True)),
                ('mobilenumber_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MobileNumber_Sec1', max_length=50, null=True)),
                ('landlineno_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Landlineno_Sec1', max_length=50, null=True)),
                ('consumption_date', models.DateField(blank=True, db_column='Consumption_Date', null=True)),
                ('desicow_heiferno_sec1', models.IntegerField(blank=True, db_column='DesiCow_Heiferno_Sec1', null=True)),
                ('desicow_dryno_sec1', models.IntegerField(blank=True, db_column='DesiCow_DryNo_Sec1', null=True)),
                ('desicow_inmilkno_sec1', models.IntegerField(blank=True, db_column='DesiCow_InMilkNo_Sec1', null=True)),
                ('crossbred_heiferno_sec1', models.IntegerField(blank=True, db_column='Crossbred_Heiferno_Sec1', null=True)),
                ('crossbred_dryno_sec1', models.IntegerField(blank=True, db_column='Crossbred_Dryno_Sec1', null=True)),
                ('crossbred_inmilkno_sec1', models.IntegerField(blank=True, db_column='Crossbred_InMilkno_Sec1', null=True)),
                ('buffalo_heiferno_sec1', models.IntegerField(blank=True, db_column='Buffalo_Heiferno_Sec1', null=True)),
                ('buffalo_dryno_sec1', models.IntegerField(blank=True, db_column='Buffalo_Dryno_Sec1', null=True)),
                ('buffalo_inmilkno_sec1', models.IntegerField(blank=True, db_column='Buffalo_InMilkno_Sec1', null=True)),
                ('lpd', models.IntegerField(blank=True, db_column='LPD', null=True)),
                ('household_consumption_sec1', models.IntegerField(blank=True, db_column='Household_Consumption_Sec1', null=True)),
                ('markatable_surplus_sec1', models.IntegerField(blank=True, db_column='Markatable_surplus_Sec1', null=True)),
                ('nm_saving_ac', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nm_Saving_Ac', max_length=50, null=True)),
                ('saving_ac_no', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Saving_Ac_No', max_length=50, null=True)),
                ('bank_name_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Bank_Name_Sec2', max_length=50, null=True)),
                ('branch_name_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Branch_Name_Sec2', max_length=50, null=True)),
                ('partcu_nm1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm1', max_length=50, null=True)),
                ('partcu_nm1_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm1_Gen', max_length=20, null=True)),
                ('partcu_nm1_age', models.IntegerField(blank=True, db_column='Partcu_Nm1_Age', null=True)),
                ('partcu_nm1_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm1_Rel', max_length=50, null=True)),
                ('partcu_nm2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm2', max_length=50, null=True)),
                ('partcu_nm2_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm2_Gen', max_length=20, null=True)),
                ('partcu_nm2_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm2_Rel', max_length=50, null=True)),
                ('partcu_nm2_age', models.IntegerField(blank=True, db_column='Partcu_Nm2_Age', null=True)),
                ('partcu_nm3', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm3', max_length=50, null=True)),
                ('partcu_nm3_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm3_Gen', max_length=20, null=True)),
                ('partcu_nm3_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm3_Rel', max_length=20, null=True)),
                ('partcu_nm3_age', models.IntegerField(blank=True, db_column='Partcu_Nm3_Age', null=True)),
                ('partcu_nm4', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm4', max_length=50, null=True)),
                ('partcu_nm4_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm4_Gen', max_length=20, null=True)),
                ('partcu_nm4_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm4_Rel', max_length=20, null=True)),
                ('partcu_nm4_age', models.IntegerField(blank=True, db_column='Partcu_Nm4_Age', null=True)),
                ('partcu_nm5', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm5', max_length=50, null=True)),
                ('partcu_nm5_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm5_Gen', max_length=20, null=True)),
                ('partcu_nm5_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm5_Rel', max_length=20, null=True)),
                ('partcu_nm5_age', models.IntegerField(blank=True, db_column='Partcu_Nm5_Age', null=True)),
                ('partcu_nm6', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm6', max_length=50, null=True)),
                ('partcu_nm6_gen', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm6_Gen', max_length=20, null=True)),
                ('partcu_nm6_rel', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Partcu_Nm6_Rel', max_length=20, null=True)),
                ('partcu_nm6_age', models.IntegerField(blank=True, db_column='Partcu_Nm6_Age', null=True)),
                ('nominee_nm_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nominee_Nm_Sec2', max_length=50, null=True)),
                ('relationwith_nominee_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Relationwith_Nominee_Sec2', max_length=50, null=True)),
                ('nominee_address', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nominee_Address', max_length=50, null=True)),
                ('nominee_guardiannm_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nominee_GuardianNm_Sec2', max_length=50, null=True)),
                ('nominee_dob_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nominee_DOB_Sec2', max_length=50, null=True)),
                ('mcc_name_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MCC_Name_Sec2', max_length=50, null=True)),
                ('mcc_code_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MCC_CODE_Sec2', max_length=10, null=True)),
                ('mpp_nm_sec2', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Mpp_Nm_Sec2', null=True)),
                ('mpp_code_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Mpp_Code_Sec2', max_length=10, null=True)),
                ('rev_vill_nm_sec2', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Rev_Vill_Nm_Sec2', null=True)),
                ('rev_vill_code_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Rev_Vill_Code_Sec2', max_length=8, null=True)),
                ('tehsil_nm_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Tehsil_Nm_Sec2', max_length=50, null=True)),
                ('distirict_nm_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Distirict_Nm_Sec2', max_length=50, null=True)),
                ('poolingpoint_code_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='PoolingPoint_Code_Sec2', max_length=10, null=True)),
                ('hamlet_name_sec2', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Hamlet_Name_Sec2', null=True)),
                ('aadhar_card_no_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Aadhar_Card_No_Sec2', max_length=12, null=True)),
                ('addmission_fee_sec3', models.IntegerField(blank=True, db_column='Addmission_Fee_Sec3', null=True)),
                ('share_qty_sec3', models.IntegerField(blank=True, db_column='Share_Qty_Sec3', null=True)),
                ('received_amt_sec3', models.IntegerField(blank=True, db_column='Received_Amt_Sec3', null=True)),
                ('cashdd_sec3', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='CashDD_Sec3', max_length=50, null=True)),
                ('bank_name_sec3', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Bank_Name_Sec3', max_length=50, null=True)),
                ('branch_name_sec3', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Branch_Name_Sec3', max_length=50, null=True)),
                ('ddnumber_sec3', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='DDNumber_Sec3', max_length=50, null=True)),
                ('dddate_sec3', models.DateField(blank=True, db_column='DDDate_Sec3', null=True)),
                ('amount_sec3', models.IntegerField(blank=True, db_column='Amount_Sec3', null=True)),
                ('userid', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UserId', max_length=50, null=True)),
                ('entrydate', models.DateTimeField(blank=True, db_column='Entrydate', null=True)),
                ('ifscode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='IFSCODE', max_length=50, null=True)),
                ('membercode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MemberCode', max_length=16, null=True)),
                ('hamlet_code', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Hamlet_Code', max_length=2, null=True)),
                ('shg_member', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='SHG_MEMBER', max_length=5, null=True)),
                ('is_active', models.IntegerField(blank=True, db_column='IS_ACTIVE', null=True)),
                ('updateddt', models.DateTimeField(blank=True, db_column='UpdatedDt', null=True)),
                ('updatedby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UpdatedBy', max_length=50, null=True)),
                ('acceptedby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='AcceptedBy', max_length=50, null=True)),
                ('ce_approval_date', models.DateField(blank=True, db_column='CE_approval_Date', null=True)),
                ('board_approval_date', models.DateField(blank=True, db_column='Board_approval_Date', null=True)),
                ('cancelled_surrendered_date', models.DateField(blank=True, db_column='Cancelled_Surrendered_Date', null=True)),
                ('code_activation_date', models.DateField(blank=True, db_column='Code_Activation_Date', null=True)),
                ('folio_no', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Folio_No', max_length=10, null=True)),
                ('member_unique_code', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Member_Unique_Code', max_length=50, null=True)),
                ('remarks', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Remarks', max_length=100, null=True)),
                ('membercode_transfer_dt', models.DateTimeField(blank=True, db_column='MemberCode_Transfer_Dt', null=True)),
                ('supervisornm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='SupervisorNm', max_length=50, null=True)),
            ],
            options={
                'db_table': 'entry_table',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='EntrytableHis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membercode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Membercode', max_length=16, null=True)),
                ('formnumber', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FormNumber', max_length=10, null=True)),
                ('applicantnm_sec1', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='ApplicantNm_Sec1', max_length=50, null=True)),
                ('nm_saving_ac', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Nm_Saving_Ac', max_length=50, null=True)),
                ('saving_ac_no', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Saving_Ac_No', max_length=50, null=True)),
                ('bank_name_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Bank_Name_Sec2', max_length=50, null=True)),
                ('branch_name_sec2', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Branch_Name_Sec2', max_length=50, null=True)),
                ('ifscode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='IFSCODE', max_length=50, null=True)),
                ('userid', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UserId', max_length=50, null=True)),
                ('entrydate', models.DateTimeField(blank=True, db_column='Entrydate', null=True)),
                ('updateddt', models.DateTimeField(blank=True, db_column='UpdatedDt', null=True)),
                ('updatedby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UpdatedBy', max_length=50, null=True)),
            ],
            options={
                'db_table': 'EntryTable_his',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='FolioDetails',
            fields=[
                ('fid', models.AutoField(db_column='Fid', primary_key=True, serialize=False)),
                ('foliono', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FolioNo', max_length=50, null=True)),
                ('no_of_shares_alloted_by_board', models.IntegerField(blank=True, db_column='No_of_shares_alloted_by_Board', null=True)),
                ('shared_alloted_date', models.DateField(blank=True, db_column='Shared_alloted_date', null=True)),
                ('created', models.DateTimeField(blank=True, db_column='Created', null=True)),
                ('createdby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='CreatedBy', max_length=50, null=True)),
                ('member_unique_code', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Member_Unique_Code', max_length=50, null=True)),
            ],
            options={
                'db_table': 'Folio_Details',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MemberActiveDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membercode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Membercode', max_length=16, null=True)),
                ('member_unique_code', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Member_Unique_Code', max_length=100, null=True)),
                ('bmccode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', max_length=20, null=True)),
                ('ppcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', max_length=20, null=True)),
                ('bmcname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='bmcName', max_length=20, null=True)),
                ('ppname', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='PPName', max_length=50, null=True)),
            ],
            options={
                'db_table': 'Member_Active_Details',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MemberAnimalDetails',
            fields=[
                ('did', models.AutoField(db_column='Did', primary_key=True, serialize=False)),
                ('member_unique_code', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Member_Unique_Code', max_length=50, null=True)),
                ('formno', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FormNo', max_length=50, null=True)),
                ('mcccode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MccCode', max_length=50, null=True)),
                ('mppcode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MppCode', max_length=50, null=True)),
                ('membercode', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MemberCode', max_length=50, null=True)),
                ('mobileno', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MobileNo', max_length=50, null=True)),
                ('membernm', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='MemberNm', max_length=50, null=True)),
                ('animalid', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='AnimalId', max_length=50, null=True)),
                ('species', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Species', max_length=50, null=True)),
                ('breed', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='Breed', max_length=50, null=True)),
                ('age', models.IntegerField(blank=True, db_column='Age', null=True)),
                ('milkqty', models.DecimalField(blank=True, db_column='MilkQty', decimal_places=2, max_digits=10, null=True)),
                ('milklastlactation', models.DecimalField(blank=True, db_column='MilkLastLactation', decimal_places=2, max_digits=10, null=True)),
                ('inmilk', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='InMilk', max_length=50, null=True)),
                ('datelastcalving', models.DateField(blank=True, db_column='DateLastCalving', null=True)),
                ('datelastai', models.DateField(blank=True, db_column='DateLastAI', null=True)),
                ('areafodder', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='AreaFodder', max_length=50, null=True)),
                ('userid', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UserId', max_length=50, null=True)),
                ('entrydate', models.DateTimeField(blank=True, db_column='Entrydate', null=True)),
                ('updateddt', models.DateTimeField(blank=True, db_column='UpdatedDt', null=True)),
                ('updatedby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='UpdatedBy', max_length=50, null=True)),
            ],
            options={
                'db_table': 'Member_Animal_details',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Tbllog',
            fields=[
                ('logid', models.AutoField(db_column='LogId', primary_key=True, serialize=False)),
                ('formno', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='FormNo', max_length=50, null=True)),
                ('errormsg', models.TextField(blank=True, db_collation='Latin1_General_CI_AI', db_column='ErrorMsg', null=True)),
                ('createddt', models.DateTimeField(blank=True, db_column='CreatedDt', null=True)),
                ('createdby', models.CharField(blank=True, db_collation='Latin1_General_CI_AI', db_column='CreatedBy', max_length=50, null=True)),
            ],
            options={
                'db_table': 'TblLog',
                'managed': False,
            },
        ),
    ]