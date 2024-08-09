# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Masteruser(models.Model):
    uid = models.AutoField(db_column='Uid', primary_key = True)  # Field name made lowercase.
    usertypecode = models.CharField(db_column='USERTYPECODE', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    username = models.CharField(db_column='USERNAME', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    userlogincode = models.CharField(db_column='USERloginCODE', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    userpwd = models.CharField(db_column='USERPWD', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    plantcode = models.CharField(db_column='PlantCode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcccode = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    bmccode = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    ppcode = models.CharField(db_column='PPcode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    createdon = models.DateTimeField(blank=True, null=True)
    updatedby = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    user_level = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    login_flag = models.BooleanField(blank=True, null=True)
    current_ip = models.CharField(max_length=16, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    mobno = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    photopath = models.CharField(db_column='PhotoPath', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    companycode = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MASTERUSER'


class Mappsmsotp(models.Model):
    rowid = models.AutoField(db_column='Rowid',primary_key = True)  # Field name made lowercase.
    phone = models.TextField(db_collation='Latin1_General_CI_AI', blank=True, null=True)
    otp = models.TextField(db_column='OTP', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateField(db_column='Cdate', blank=True, null=True)  # Field name made lowercase.
    ctime = models.TimeField(db_column='Ctime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MAppSMSOTP'


class Permissionmaster(models.Model):
    permissionid = models.BigIntegerField(db_column='PermissionID', primary_key = True)  # Field name made lowercase.
    controller = models.CharField(db_column='Controller', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    action = models.CharField(db_column='Action', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mainpagenm = models.CharField(db_column='MainPageNm', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    actiondispnm = models.CharField(db_column='ActionDispNm', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    createddt = models.DateTimeField(db_column='CreatedDt', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PermissionMaster'


class TblAnimalTransaction(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    bmccode = models.CharField(db_column='BMCCode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    head_type = models.CharField(db_column='Head Type', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    mp_code = models.CharField(db_column='MP Code', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    mp_name = models.CharField(db_column='MP Name', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    qty = models.IntegerField(db_column='QTY', blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    from_date = models.DateTimeField(db_column='From_Date', blank=True, null=True)  # Field name made lowercase.
    to_date = models.DateTimeField(db_column='To_date', blank=True, null=True)  # Field name made lowercase.
    transaction_status = models.IntegerField(db_column='Transaction_status', blank=True, null=True)  # Field name made lowercase.
    balance_due = models.DecimalField(db_column='Balance_due', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    createddt = models.DateTimeField(db_column='createdDt', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='updatedDt', blank=True, null=True)  # Field name made lowercase.
    ppcode = models.CharField(db_column='PPCODE', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    entryby = models.CharField(db_column='EntryBy', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_Animal_Transaction'


class TblCashreturnhold(models.Model):
    cashid = models.AutoField(db_column='CashId', primary_key=True)  # Field name made lowercase.
    membercode = models.CharField(db_column='MemberCode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    paymentcycle_fromdt = models.DateField(db_column='PaymentCycle_FromDt', blank=True, null=True)  # Field name made lowercase.
    paymentcycle_todt = models.DateField(db_column='PaymentCycle_ToDt', blank=True, null=True)  # Field name made lowercase.
    hold_return_amount = models.DecimalField(db_column='Hold/Return Amount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    type = models.CharField(db_column='Type', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    createddt = models.DateTimeField(db_column='CreatedDt', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.
    payment_releasedate = models.DateField(db_column='Payment_ReleaseDate', blank=True, null=True)  # Field name made lowercase.
    membername = models.CharField(db_column='MemberName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ppcode = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    bmccode = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    releasedby = models.CharField(db_column='ReleasedBy', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_CashReturnHold'


class TblCashreturnholdBkp141122(models.Model):
    cashid = models.AutoField(db_column='CashId',primary_key = True)  # Field name made lowercase.
    membercode = models.CharField(db_column='MemberCode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    paymentcycle_fromdt = models.DateField(db_column='PaymentCycle_FromDt', blank=True, null=True)  # Field name made lowercase.
    paymentcycle_todt = models.DateField(db_column='PaymentCycle_ToDt', blank=True, null=True)  # Field name made lowercase.
    hold_return_amount = models.DecimalField(db_column='Hold/Return Amount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    type = models.CharField(db_column='Type', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    createddt = models.DateTimeField(db_column='CreatedDt', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.
    payment_releasedate = models.DateField(db_column='Payment_ReleaseDate', blank=True, null=True)  # Field name made lowercase.
    membername = models.CharField(db_column='MemberName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ppcode = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    bmccode = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    createdby = models.CharField(db_column='CreatedBy', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    releasedby = models.CharField(db_column='ReleasedBy', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_CashReturnHold_bkp141122'


class TblMemberdeductionDetails(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key = True)  # Field name made lowercase.
    mcc_code = models.CharField(db_column='MCC_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_code = models.CharField(db_column='MPP_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    membercode = models.CharField(db_column='MEMBERCODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    opening_balance = models.DecimalField(db_column='OPENING_BALANCE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    deduction = models.DecimalField(db_column='DEDUCTION', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    balance = models.DecimalField(db_column='BALANCE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paid_amount = models.DecimalField(db_column='PAID_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    payment_cycle_from_dt = models.DateTimeField(db_column='PAYMENT_CYCLE_FROM_DT', blank=True, null=True)  # Field name made lowercase.
    payment_cycle_to_dt = models.DateTimeField(db_column='PAYMENT_CYCLE_TO_DT', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='STATUS', blank=True, null=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='CREATE_DATE', blank=True, null=True)  # Field name made lowercase.
    update_date = models.DateTimeField(db_column='UPDATE_DATE', blank=True, null=True)  # Field name made lowercase.
    balance_qty = models.DecimalField(db_column='Balance_qty', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_sale_amount = models.DecimalField(db_column='TOTAL_SALE_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_unique_code = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    total_days = models.IntegerField(db_column='TOTAL_DAYS', blank=True, null=True)  # Field name made lowercase.
    f_year = models.CharField(db_column='F_YEAR', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fy_qtylastyear = models.DecimalField(db_column='FY_QTYLastYear', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_MemberDeduction_Details'


class TblMemberdeductionDetailsBkp12Apr(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key = True)  # Field name made lowercase.
    mcc_code = models.CharField(db_column='MCC_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_code = models.CharField(db_column='MPP_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    membercode = models.CharField(db_column='MEMBERCODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    opening_balance = models.DecimalField(db_column='OPENING_BALANCE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    deduction = models.DecimalField(db_column='DEDUCTION', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    balance = models.DecimalField(db_column='BALANCE', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paid_amount = models.DecimalField(db_column='PAID_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    payment_cycle_from_dt = models.DateTimeField(db_column='PAYMENT_CYCLE_FROM_DT', blank=True, null=True)  # Field name made lowercase.
    payment_cycle_to_dt = models.DateTimeField(db_column='PAYMENT_CYCLE_TO_DT', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='STATUS', blank=True, null=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='CREATE_DATE', blank=True, null=True)  # Field name made lowercase.
    update_date = models.DateTimeField(db_column='UPDATE_DATE', blank=True, null=True)  # Field name made lowercase.
    balance_qty = models.DecimalField(db_column='Balance_qty', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_sale_amount = models.DecimalField(db_column='TOTAL_SALE_AMOUNT', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_unique_code = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    total_days = models.IntegerField(db_column='TOTAL_DAYS', blank=True, null=True)  # Field name made lowercase.
    f_year = models.CharField(db_column='F_YEAR', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_MemberDeduction_Details_bkp12apr'


class TblMpmsuserpermission(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    loginid = models.IntegerField(db_column='LoginId', blank=True, null=True)  # Field name made lowercase.
    pageid = models.IntegerField(db_column='PageId', blank=True, null=True)  # Field name made lowercase.
    createddt = models.DateTimeField(db_column='CreatedDt', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isselected = models.BooleanField(db_column='IsSelected', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_MpmsUserPermission'


class TblPageurl(models.Model):
    pageid = models.AutoField(primary_key=True)
    pagename = models.CharField(db_column='Pagename', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pageurl = models.CharField(db_column='PageUrl', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    isselected = models.BooleanField(db_column='IsSelected', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_PageURL'


class TblRatemaster(models.Model):
    rid = models.AutoField(db_column='Rid', primary_key=True)  # Field name made lowercase.
    headtype = models.CharField(db_column='HeadType', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    activedate = models.DateField(db_column='ActiveDate', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_RateMaster'


class TblUserLogin(models.Model):
    login_id = models.AutoField(db_column='Login_ID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pwd = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    bmccode = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    createddate = models.DateTimeField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    updateddt = models.DateTimeField(db_column='UpdatedDt', blank=True, null=True)  # Field name made lowercase.
    ppcode = models.TextField(db_column='PPCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tbl_User_Login'


class Test1(models.Model):
    collectioncode = models.BigIntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    dump_date = models.DateField(db_column='Dump_Date', blank=True, null=True)  # Field name made lowercase.
    company_code = models.BigIntegerField(db_column='Company_Code', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Test1'


class Test3(models.Model):
    islabmanual = models.BooleanField(db_column='IslabManual', blank=True, null=True)  # Field name made lowercase.
    urea = models.CharField(db_column='Urea', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.CharField(db_column='Maltodex', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.CharField(db_column='Sucrose', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.CharField(db_column='Ammsulp', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    remark_lab = models.CharField(db_column='Remark_Lab', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    company_code = models.BigIntegerField(db_column='Company_Code', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Test3'


class UserPermission(models.Model):
    rowid = models.BigAutoField(db_column='RowID',primary_key=True)  # Field name made lowercase.
    usertypecode = models.CharField(db_column='USERTYPECODE', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    permissionid = models.BigIntegerField(db_column='PermissionID', blank=True, null=True)  # Field name made lowercase.
    allow = models.IntegerField(db_column='Allow', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'USER_PERMISSION'


class Usergroup(models.Model):
    usertypecode = models.CharField(db_column='USERTYPECODE', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    usertypedesc = models.CharField(db_column='USERTYPEDESC', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updateby = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    grouptype = models.CharField(db_column='GROUPTYPE', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    userlevel = models.CharField(db_column='UserLevel', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Usergroup'


class AuthTokenMaster(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    user_id = models.IntegerField(blank=True, null=True)
    token = models.TextField(db_collation='Latin1_General_CI_AI', blank=True, null=True)
    refresh_token = models.TextField(db_collation='Latin1_General_CI_AI', blank=True, null=True)
    token_date_time = models.DateTimeField(blank=True, null=True)
    is_alive = models.BooleanField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_token_master'


class OldTblsmssetting(models.Model):
    id = models.BigAutoField(primary_key=True)
    smsurl = models.TextField(db_column='SMSURL', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    username = models.TextField(db_column='USERNAME', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    password = models.TextField(db_column='PASSWORD', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gsmid = models.TextField(db_column='GSMID', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mt = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    companycode = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    balanceurl = models.TextField(db_column='BalanceUrl', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    responseurl = models.TextField(db_column='ResponseUrl', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    templateid = models.CharField(db_column='TemplateId', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'old_tblSmsSetting'


class Rowdata(models.Model):
    bmccode = models.BigIntegerField(blank=True, null=True)
    ppcode = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_code = models.CharField(db_column='MEMBER_CODE', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=38, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=38, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_days = models.IntegerField(db_column='Total_Days', blank=True, null=True)  # Field name made lowercase.
    member_unique_code = models.CharField(db_column='Member_Unique_Code', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rowdata'


class RowdataAll(models.Model):
    bmccode = models.BigIntegerField(blank=True, null=True)
    ppcode = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_code = models.CharField(db_column='MEMBER_CODE', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=38, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=38, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_days = models.IntegerField(db_column='Total_Days', blank=True, null=True)  # Field name made lowercase.
    member_unique_code = models.CharField(db_column='Member_Unique_Code', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rowdata_all'


class RowdataAllSub(models.Model):
    bmccode = models.BigIntegerField(blank=True, null=True)
    ppcode = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_code = models.CharField(db_column='MEMBER_CODE', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=38, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=38, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_days = models.IntegerField(db_column='Total_Days', blank=True, null=True)  # Field name made lowercase.
    member_unique_code = models.CharField(db_column='Member_Unique_Code', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rowdata_all_sub'


class RowdataSub(models.Model):
    bmccode = models.BigIntegerField(blank=True, null=True)
    ppcode = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    member_code = models.CharField(db_column='MEMBER_CODE', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    total_qty = models.DecimalField(db_column='TOTAL_QTY', max_digits=38, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    total_amount = models.DecimalField(db_column='TOTAL_AMOUNT', max_digits=38, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_days = models.IntegerField(db_column='Total_Days', blank=True, null=True)  # Field name made lowercase.
    member_unique_code = models.CharField(db_column='Member_Unique_Code', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rowdata_sub'


class Tblactualdate(models.Model):
    date = models.DateField(db_column='DATE', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='SHIFT', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcc_id = models.IntegerField(db_column='MCC_Id', blank=True, null=True)  # Field name made lowercase.
    bmc_id = models.IntegerField(db_column='BMC_Id', blank=True, null=True)  # Field name made lowercase.
    mccname = models.CharField(db_column='MCCName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcname = models.CharField(db_column='BMCName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    vlccid = models.BigIntegerField(db_column='VLCCId', blank=True, null=True)  # Field name made lowercase.
    mpp_name = models.CharField(db_column='MPP_Name', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cqty = models.DecimalField(db_column='CQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfatkg = models.DecimalField(db_column='CFatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    csnfkg = models.DecimalField(db_column='CSNFKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfat = models.DecimalField(db_column='CFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    csnf = models.DecimalField(db_column='CSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dqty = models.DecimalField(db_column='DQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dfatkg = models.DecimalField(db_column='dFatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    dsnfkg = models.DecimalField(db_column='dSNFKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    dfat = models.DecimalField(db_column='dFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dsnf = models.DecimalField(db_column='dSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    damount = models.DecimalField(db_column='dAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    aqty = models.DecimalField(db_column='AQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    afatkg = models.DecimalField(db_column='AFatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    asnfkg = models.DecimalField(db_column='ASNFKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    afat = models.DecimalField(db_column='AFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    asnf = models.DecimalField(db_column='ASNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    aamount = models.DecimalField(db_column='AAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cd_qty = models.DecimalField(db_column='CD_Qty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cd_fatkg = models.DecimalField(db_column='CD_FatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    cd_snfkg = models.DecimalField(db_column='CD_SnfKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    cd_fat = models.DecimalField(db_column='CD_Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cd_snf = models.DecimalField(db_column='CD_SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cd_amount = models.DecimalField(db_column='CD_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    da_qty = models.DecimalField(db_column='DA_Qty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    da_fatkg = models.DecimalField(db_column='DA_FatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    da_snfkg = models.DecimalField(db_column='DA_SnfKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    da_fat = models.DecimalField(db_column='DA_Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    da_snf = models.DecimalField(db_column='DA_Snf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    da_amount = models.DecimalField(db_column='DA_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ca_qty = models.DecimalField(db_column='CA_Qty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ca_fatkg = models.DecimalField(db_column='CA_FatKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ca_snfkg = models.DecimalField(db_column='CA_SnfKg', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ca_fat = models.DecimalField(db_column='CA_Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ca_snf = models.DecimalField(db_column='CA_Snf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ca_amount = models.DecimalField(db_column='CA_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    cattle_type_actual_amount = models.DecimalField(db_column='Cattle_Type_Actual_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cattle_type_dispatch_amount = models.DecimalField(db_column='Cattle_Type_Dispatch_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cattle_type_cd_amount = models.DecimalField(db_column='Cattle_Type_CD_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cattle_type_da_amount = models.DecimalField(db_column='Cattle_Type_DA_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cattle_type_ca_amount = models.DecimalField(db_column='Cattle_Type_CA_Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblActualDate'


class Tblanalyserdefinition(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    analyserid = models.IntegerField(db_column='AnalyserId', blank=True, null=True)  # Field name made lowercase.
    parameterdesc = models.CharField(db_column='ParameterDesc', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAnalyserDefinition'


class Tblappuser(models.Model):
    usercode = models.BigIntegerField(db_column='userCode', primary_key=True)  # Field name made lowercase. The composite primary key (userCode, societyCode, smpsId) found, that is not supported. The first column is selected.
    firstname = models.CharField(db_column='firstName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    middlename = models.CharField(db_column='middleName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode')  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    userpassword = models.CharField(db_column='userPassword', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(max_length=7, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    isdownloaded = models.BooleanField(db_column='isDownloaded', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblAppUser'
        unique_together = (('usercode', 'societycode', 'smpsid'),)


class Tblbackenderror(models.Model):
    errorid = models.BigAutoField(db_column='ErrorId', primary_key=True)  # Field name made lowercase.
    errorlineno = models.TextField(db_column='ErrorLineNo', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errormessage = models.TextField(db_column='ErrorMessage', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errortype = models.TextField(db_column='ErrorType', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorstacktrace = models.TextField(db_column='ErrorStackTrace', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorlocation = models.TextField(db_column='ErrorLocation', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errordatetime = models.DateTimeField(db_column='ErrorDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblBackendError'


class Tblbankdetail(models.Model):
    bankdetailcode = models.IntegerField(db_column='BankDetailCode', primary_key=True)  # Field name made lowercase.
    bankcode = models.ForeignKey('Tblmstbank', models.DO_NOTHING, db_column='BankCode', blank=True, null=True)  # Field name made lowercase.
    branchname = models.CharField(db_column='BranchName', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsccode = models.CharField(db_column='IfscCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.ForeignKey('Tblcountry', models.DO_NOTHING, db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='Pincode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblBankDetail'


class Tblbankftpcredmanager(models.Model):
    rowid = models.BigAutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    ftpcredid = models.BigIntegerField(db_column='ftpCredId')  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    paymentpartnerid = models.BigIntegerField(db_column='paymentPartnerId', blank=True, null=True)  # Field name made lowercase.
    ftpurl = models.CharField(db_column='ftpUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ftpusername = models.CharField(db_column='ftpUsername', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ftppassword = models.CharField(db_column='ftpPassword', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='isDeleted', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDatetime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblBankFtpCredManager'


class Tblchildmenu(models.Model):
    childid = models.IntegerField(db_column='ChildId', primary_key=True)  # Field name made lowercase.
    parentid = models.ForeignKey('Tblparentmenu', models.DO_NOTHING, db_column='ParentId', blank=True, null=True)  # Field name made lowercase.
    childdesc = models.TextField(db_column='ChildDesc', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    childnavigation = models.TextField(db_column='ChildNavigation', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblChildMenu'


class Tblchildmenu2(models.Model):
    childid = models.IntegerField(db_column='ChildId', primary_key=True)  # Field name made lowercase.
    parentid = models.ForeignKey('Tblparentmenu', models.DO_NOTHING, db_column='ParentId', blank=True, null=True)  # Field name made lowercase.
    childdesc = models.TextField(db_column='ChildDesc', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    childnavigation = models.TextField(db_column='ChildNavigation', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblChildMenu2'


class Tblcollection(models.Model):
    rawid = models.DecimalField(db_column='RawId', primary_key=True, max_digits=30, decimal_places=0)  # Field name made lowercase. The composite primary key (RawId, AutoID, DumpDate, Shift, SampleId, rtCode, DockNo, cntcode, CollectionCode, CompanyCode) found, that is not supported. The first column is selected.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    brate = models.DecimalField(db_column='BRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crate = models.DecimalField(db_column='CRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mrate = models.DecimalField(db_column='Mrate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bamount = models.DecimalField(db_column='BAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mamount = models.DecimalField(db_column='MAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalamount = models.DecimalField(db_column='TotalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId')  # Field name made lowercase.
    rtcode = models.BigIntegerField(db_column='rtCode')  # Field name made lowercase.
    soccode = models.BigIntegerField()
    socname = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightltr = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    rcans = models.IntegerField(db_column='rCans', blank=True, null=True)  # Field name made lowercase.
    acans = models.IntegerField(db_column='aCans', blank=True, null=True)  # Field name made lowercase.
    avgfat = models.DecimalField(db_column='avgFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    avgsnf = models.DecimalField(db_column='avgSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(db_column='Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lr = models.DecimalField(db_column='LR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    protein = models.DecimalField(db_column='Protein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lactose = models.DecimalField(db_column='Lactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo')  # Field name made lowercase.
    dumptime = models.DateTimeField(db_column='DumpTime', blank=True, null=True)  # Field name made lowercase.
    testtime = models.DateTimeField(db_column='TestTime', blank=True, null=True)  # Field name made lowercase.
    did = models.IntegerField(db_column='DId', blank=True, null=True)  # Field name made lowercase.
    ddate = models.DateTimeField(db_column='DDate', blank=True, null=True)  # Field name made lowercase.
    lid = models.IntegerField(db_column='LId', blank=True, null=True)  # Field name made lowercase.
    ldate = models.DateTimeField(db_column='LDate', blank=True, null=True)  # Field name made lowercase.
    ismanuallab = models.BooleanField(blank=True, null=True)
    ismanualwt = models.BooleanField(blank=True, null=True)
    rttenkercode = models.IntegerField(blank=True, null=True)
    socpurchase = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    remarkdock = models.TextField(db_column='remarkDock', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    remarklab = models.TextField(db_column='remarkLAB', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lid1 = models.IntegerField(db_column='LId1', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField()
    collectioncode = models.BigIntegerField(db_column='CollectionCode')  # Field name made lowercase.
    companycode = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='CompanyCode')  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    history = models.IntegerField(db_column='History', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isskip = models.BooleanField(db_column='IsSkip', blank=True, null=True)  # Field name made lowercase.
    sampleno = models.BigIntegerField(db_column='SampleNo', blank=True, null=True)  # Field name made lowercase.
    density = models.DecimalField(db_column='Density', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.DecimalField(db_column='FreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    water = models.CharField(db_column='Water', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    urea = models.CharField(db_column='Urea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.CharField(db_column='Maltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.CharField(db_column='Ammsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.CharField(db_column='Sucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.CharField(db_column='Abnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    badsample = models.CharField(db_column='BadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightrejected = models.DecimalField(db_column='WeightRejected', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isprocessed = models.BooleanField(db_column='IsProcessed', blank=True, null=True)  # Field name made lowercase.
    dockpublicip = models.CharField(db_column='DockPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    labpublicip = models.CharField(db_column='LabPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='AutoID')  # Field name made lowercase.
    istested = models.BooleanField(db_column='IsTested', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCollection'
        unique_together = (('rawid', 'autoid', 'dumpdate', 'shift', 'sampleid', 'rtcode', 'dockno', 'cntcode', 'collectioncode', 'companycode'),)


class Tblcollection2(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    brate = models.DecimalField(db_column='BRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crate = models.DecimalField(db_column='CRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mrate = models.DecimalField(db_column='Mrate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bamount = models.DecimalField(db_column='BAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mamount = models.DecimalField(db_column='MAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalamount = models.DecimalField(db_column='TotalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId')  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='rtCode', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(blank=True, null=True)
    socname = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightltr = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    rcans = models.IntegerField(db_column='rCans', blank=True, null=True)  # Field name made lowercase.
    acans = models.IntegerField(db_column='aCans', blank=True, null=True)  # Field name made lowercase.
    avgfat = models.DecimalField(db_column='avgFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    avgsnf = models.DecimalField(db_column='avgSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(db_column='Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lr = models.DecimalField(db_column='LR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    protein = models.DecimalField(db_column='Protein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lactose = models.DecimalField(db_column='Lactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.DateTimeField(db_column='DumpTime', blank=True, null=True)  # Field name made lowercase.
    testtime = models.DateTimeField(db_column='TestTime', blank=True, null=True)  # Field name made lowercase.
    did = models.IntegerField(db_column='DId', blank=True, null=True)  # Field name made lowercase.
    ddate = models.DateTimeField(db_column='DDate', blank=True, null=True)  # Field name made lowercase.
    lid = models.IntegerField(db_column='LId', blank=True, null=True)  # Field name made lowercase.
    ldate = models.DateTimeField(db_column='LDate', blank=True, null=True)  # Field name made lowercase.
    ismanuallab = models.BooleanField(blank=True, null=True)
    ismanualwt = models.BooleanField(blank=True, null=True)
    rttenkercode = models.IntegerField(blank=True, null=True)
    socpurchase = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    remarkdock = models.TextField(db_column='remarkDock', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    remarklab = models.TextField(db_column='remarkLAB', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lid1 = models.IntegerField(db_column='LId1', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(blank=True, null=True)
    collectioncode = models.IntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    history = models.IntegerField(db_column='History', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isskip = models.BooleanField(db_column='IsSkip', blank=True, null=True)  # Field name made lowercase.
    sampleno = models.BigIntegerField(db_column='SampleNo', blank=True, null=True)  # Field name made lowercase.
    density = models.DecimalField(db_column='Density', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.DecimalField(db_column='FreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    water = models.CharField(db_column='Water', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    urea = models.CharField(db_column='Urea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.CharField(db_column='Maltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.CharField(db_column='Ammsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.CharField(db_column='Sucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.CharField(db_column='Abnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    badsample = models.CharField(db_column='BadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightrejected = models.DecimalField(db_column='WeightRejected', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isprocessed = models.BooleanField(db_column='IsProcessed', blank=True, null=True)  # Field name made lowercase.
    dockpublicip = models.CharField(db_column='DockPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    labpublicip = models.CharField(db_column='LabPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCollection2'


class Tblcollectionlog(models.Model):
    logid = models.AutoField(db_column='LogId',primary_key=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCollectionLog'


class Tblcompanysettings(models.Model):
    setting_id = models.BigIntegerField(db_column='Setting_Id', primary_key=True)  # Field name made lowercase.
    company = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='Company_Id', blank=True, null=True)  # Field name made lowercase.
    isfarmercodechanged = models.BooleanField(db_column='IsFarmerCodeChanged', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    minbufffat = models.DecimalField(db_column='minBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufffat = models.DecimalField(db_column='maxBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='minCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='maxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffsnf = models.DecimalField(db_column='minBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffsnf = models.DecimalField(db_column='maxBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowsnf = models.DecimalField(db_column='minCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='maxCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='minMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='maxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixsnf = models.DecimalField(db_column='minMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='maxMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixclr = models.DecimalField(db_column='minMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='maxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffclr = models.DecimalField(db_column='minBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffclr = models.DecimalField(db_column='maxBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowclr = models.DecimalField(db_column='minCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='maxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    israngeexclusive = models.BooleanField(db_column='isRangeExclusive', blank=True, null=True)  # Field name made lowercase.
    canwt = models.DecimalField(db_column='CanWt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isweightround = models.BooleanField(db_column='IsWeightRound', blank=True, null=True)  # Field name made lowercase.
    canaverageweight = models.DecimalField(db_column='CanAverageWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cancapacity = models.DecimalField(db_column='CanCapacity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    daysavg = models.IntegerField(db_column='DaysAvg', blank=True, null=True)  # Field name made lowercase.
    snf_formula = models.IntegerField(db_column='SNF_Formula', blank=True, null=True)  # Field name made lowercase.
    snfconst = models.DecimalField(db_column='SnfConst', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lactose = models.BooleanField(db_column='Lactose', blank=True, null=True)  # Field name made lowercase.
    protein = models.BooleanField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    water = models.BooleanField(db_column='Water', blank=True, null=True)  # Field name made lowercase.
    density = models.BooleanField(db_column='Density', blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.BooleanField(db_column='FreezingPoint', blank=True, null=True)  # Field name made lowercase.
    urea = models.BooleanField(db_column='Urea', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.BooleanField(db_column='Maltodex', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.BooleanField(db_column='Ammsulp', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.BooleanField(db_column='Sucrose', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.BooleanField(db_column='Abnormal', blank=True, null=True)  # Field name made lowercase.
    errorname = models.BooleanField(db_column='ErrorName', blank=True, null=True)  # Field name made lowercase.
    badsample = models.BooleanField(db_column='BadSample', blank=True, null=True)  # Field name made lowercase.
    isallcenterforroute = models.BooleanField(db_column='IsAllCenterForRoute', blank=True, null=True)  # Field name made lowercase.
    isfarmercollectionduplicate = models.BooleanField(db_column='IsFarmerCollectionDuplicate', blank=True, null=True)  # Field name made lowercase.
    lrrounding = models.BooleanField(db_column='LRRounding', blank=True, null=True)  # Field name made lowercase.
    allowpaymentcyclelock = models.BooleanField(db_column='AllowPaymentCycleLock', blank=True, null=True)  # Field name made lowercase.
    milkmode = models.CharField(db_column='MilkMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isvalidationapplicable = models.BooleanField(db_column='IsValidationApplicable', blank=True, null=True)  # Field name made lowercase.
    ismilkmodeforallsociety = models.BooleanField(db_column='IsMilkModeForAllSociety', blank=True, null=True)  # Field name made lowercase.
    isweightconvertltrtokg = models.BooleanField(db_column='IsWeightConvertLtrToKG', blank=True, null=True)  # Field name made lowercase.
    vlcccollectioninliter = models.BooleanField(db_column='VLCCCollectionInLiter', blank=True, null=True)  # Field name made lowercase.
    bmccollectioninliter = models.BooleanField(db_column='BMCCollectionInLiter', blank=True, null=True)  # Field name made lowercase.
    isconvertingformula = models.BooleanField(db_column='IsConvertingFormula', blank=True, null=True)  # Field name made lowercase.
    weightroundby = models.IntegerField(db_column='WeightRoundBy', blank=True, null=True)  # Field name made lowercase.
    dockafterdecimal = models.IntegerField(db_column='DockAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    fatdefaultsour = models.DecimalField(db_column='FatDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultsour = models.DecimalField(db_column='SnfDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fatdefaultcurd = models.DecimalField(db_column='FatDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultcurd = models.DecimalField(db_column='SnfDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isfatround = models.BooleanField(db_column='IsFatRound', blank=True, null=True)  # Field name made lowercase.
    fatroundingby = models.IntegerField(db_column='FatRoundingby', blank=True, null=True)  # Field name made lowercase.
    fatafterdecimal = models.IntegerField(db_column='FatAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    issnfround = models.BooleanField(db_column='IsSnfRound', blank=True, null=True)  # Field name made lowercase.
    snfroundingby = models.IntegerField(db_column='SnfRoundingby', blank=True, null=True)  # Field name made lowercase.
    snfafterdecimal = models.IntegerField(db_column='SnfAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    lrroundingby = models.IntegerField(db_column='LRRoundingby', blank=True, null=True)  # Field name made lowercase.
    lrafterdecimal = models.IntegerField(db_column='LRAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    litertokgconst = models.DecimalField(db_column='LitertoKGConst', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    kgtoliterconst = models.DecimalField(db_column='KGtoLiterConst', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightconvertingformula = models.BigIntegerField(db_column='WeightConvertingFormula', blank=True, null=True)  # Field name made lowercase.
    traysize = models.IntegerField(db_column='traySize', blank=True, null=True)  # Field name made lowercase.
    enablegovernmentbonus = models.BooleanField(db_column='enableGovernmentBonus', blank=True, null=True)  # Field name made lowercase.
    disablescreenaftercollection = models.BooleanField(db_column='disableScreenAfterCollection', blank=True, null=True)  # Field name made lowercase.
    socmaxofflinedays = models.BigIntegerField(db_column='socMaxOfflineDays', blank=True, null=True)  # Field name made lowercase.
    addeffectivedateatratemapping = models.BooleanField(db_column='addEffectivedateAtRateMapping', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCompanySettings'


class Tblcompanysettingshistory(models.Model):
    setting_id = models.BigIntegerField(db_column='Setting_Id',primary_key=True)  # Field name made lowercase.
    company_id = models.BigIntegerField(db_column='Company_Id', blank=True, null=True)  # Field name made lowercase.
    isfarmercodechanged = models.BooleanField(db_column='IsFarmerCodeChanged', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    minbufffat = models.DecimalField(db_column='minBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufffat = models.DecimalField(db_column='maxBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='minCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='maxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffsnf = models.DecimalField(db_column='minBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffsnf = models.DecimalField(db_column='maxBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowsnf = models.DecimalField(db_column='minCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='maxCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='minMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='maxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixsnf = models.DecimalField(db_column='minMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='maxMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixclr = models.DecimalField(db_column='minMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='maxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffclr = models.DecimalField(db_column='minBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffclr = models.DecimalField(db_column='maxBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowclr = models.DecimalField(db_column='minCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='maxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    israngeexclusive = models.BooleanField(db_column='isRangeExclusive', blank=True, null=True)  # Field name made lowercase.
    canwt = models.DecimalField(db_column='CanWt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isweightround = models.BooleanField(db_column='IsWeightRound', blank=True, null=True)  # Field name made lowercase.
    canaverageweight = models.DecimalField(db_column='CanAverageWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cancapacity = models.DecimalField(db_column='CanCapacity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    daysavg = models.IntegerField(db_column='DaysAvg', blank=True, null=True)  # Field name made lowercase.
    snf_formula = models.IntegerField(db_column='SNF_Formula', blank=True, null=True)  # Field name made lowercase.
    snfconst = models.DecimalField(db_column='SnfConst', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lactose = models.BooleanField(db_column='Lactose', blank=True, null=True)  # Field name made lowercase.
    protein = models.BooleanField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    water = models.BooleanField(db_column='Water', blank=True, null=True)  # Field name made lowercase.
    density = models.BooleanField(db_column='Density', blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.BooleanField(db_column='FreezingPoint', blank=True, null=True)  # Field name made lowercase.
    urea = models.BooleanField(db_column='Urea', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.BooleanField(db_column='Maltodex', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.BooleanField(db_column='Ammsulp', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.BooleanField(db_column='Sucrose', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.BooleanField(db_column='Abnormal', blank=True, null=True)  # Field name made lowercase.
    errorname = models.BooleanField(db_column='ErrorName', blank=True, null=True)  # Field name made lowercase.
    badsample = models.BooleanField(db_column='BadSample', blank=True, null=True)  # Field name made lowercase.
    isallcenterforroute = models.BooleanField(db_column='IsAllCenterForRoute', blank=True, null=True)  # Field name made lowercase.
    isfarmercollectionduplicate = models.BooleanField(db_column='IsFarmerCollectionDuplicate', blank=True, null=True)  # Field name made lowercase.
    lrrounding = models.BooleanField(db_column='LRRounding', blank=True, null=True)  # Field name made lowercase.
    allowpaymentcyclelock = models.BooleanField(db_column='AllowPaymentCycleLock', blank=True, null=True)  # Field name made lowercase.
    milkmode = models.CharField(db_column='MilkMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isvalidationapplicable = models.BooleanField(db_column='IsValidationApplicable', blank=True, null=True)  # Field name made lowercase.
    ismilkmodeforallsociety = models.BooleanField(db_column='IsMilkModeForAllSociety', blank=True, null=True)  # Field name made lowercase.
    isweightconvertltrtokg = models.BooleanField(db_column='IsWeightConvertLtrToKG', blank=True, null=True)  # Field name made lowercase.
    vlcccollectioninliter = models.BooleanField(db_column='VLCCCollectionInLiter', blank=True, null=True)  # Field name made lowercase.
    bmccollectioninliter = models.BooleanField(db_column='BMCCollectionInLiter', blank=True, null=True)  # Field name made lowercase.
    isconvertingformula = models.BooleanField(db_column='IsConvertingFormula', blank=True, null=True)  # Field name made lowercase.
    weightroundby = models.IntegerField(db_column='WeightRoundBy', blank=True, null=True)  # Field name made lowercase.
    dockafterdecimal = models.IntegerField(db_column='DockAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    fatdefaultsour = models.DecimalField(db_column='FatDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultsour = models.DecimalField(db_column='SnfDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fatdefaultcurd = models.DecimalField(db_column='FatDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultcurd = models.DecimalField(db_column='SnfDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isfatround = models.BooleanField(db_column='IsFatRound', blank=True, null=True)  # Field name made lowercase.
    fatroundingby = models.IntegerField(db_column='FatRoundingby', blank=True, null=True)  # Field name made lowercase.
    fatafterdecimal = models.IntegerField(db_column='FatAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    issnfround = models.BooleanField(db_column='IsSnfRound', blank=True, null=True)  # Field name made lowercase.
    snfroundingby = models.IntegerField(db_column='SnfRoundingby', blank=True, null=True)  # Field name made lowercase.
    snfafterdecimal = models.IntegerField(db_column='SnfAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    lrroundingby = models.IntegerField(db_column='LRRoundingby', blank=True, null=True)  # Field name made lowercase.
    lrafterdecimal = models.IntegerField(db_column='LRAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    litertokgconst = models.DecimalField(db_column='LitertoKGConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    kgtoliterconst = models.DecimalField(db_column='KGtoLiterConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    weightconvertingformula = models.BigIntegerField(db_column='WeightConvertingFormula', blank=True, null=True)  # Field name made lowercase.
    traysize = models.IntegerField(db_column='traySize', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='historyCreatedBy', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='historyTimestamp', blank=True, null=True)  # Field name made lowercase.
    disablescreenaftercollection = models.BooleanField(db_column='disableScreenAfterCollection', blank=True, null=True)  # Field name made lowercase.
    enablegovernmentbonus = models.BooleanField(db_column='enableGovernmentBonus', blank=True, null=True)  # Field name made lowercase.
    socmaxofflinedays = models.BigIntegerField(db_column='socMaxOfflineDays', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCompanySettingsHistory'


class Tblcountry(models.Model):
    countrycode = models.IntegerField(db_column='CountryCode', primary_key=True)  # Field name made lowercase.
    countryname = models.CharField(db_column='CountryName', max_length=40, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCountry'


class Tblcycle(models.Model):
    cycleid = models.BigIntegerField(db_column='CycleId', primary_key=True)  # Field name made lowercase.
    cycleno = models.IntegerField(db_column='CycleNo', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    yearcode = models.BigIntegerField(db_column='YearCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    islock = models.BooleanField(db_column='isLock', blank=True, null=True)  # Field name made lowercase.
    mcc_id = models.BigIntegerField(db_column='Mcc_Id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCycle'


class Tblcyclehistory(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    cycleid = models.BigIntegerField(db_column='CycleId', blank=True, null=True)  # Field name made lowercase.
    cycleno = models.IntegerField(db_column='CycleNo', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    yearcode = models.BigIntegerField(db_column='YearCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    islock = models.BooleanField(db_column='isLock', blank=True, null=True)  # Field name made lowercase.
    mcc_id = models.BigIntegerField(db_column='Mcc_Id', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='MDateTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCycleHistory'


class Tblcyclesum(models.Model):
    rowid = models.AutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='centerCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='routeCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode', blank=True, null=True)  # Field name made lowercase.
    cycleno = models.IntegerField(db_column='cycleNo', blank=True, null=True)  # Field name made lowercase.
    billno = models.CharField(db_column='billNo', max_length=25, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    billdatefrom = models.DateField(db_column='billDateFrom', blank=True, null=True)  # Field name made lowercase.
    bildateto = models.DateField(db_column='bilDateTo', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.BigIntegerField(db_column='bankCode', blank=True, null=True)  # Field name made lowercase.
    bankaccount = models.CharField(db_column='bankAccount', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    yearcode = models.BigIntegerField(db_column='yearCode', blank=True, null=True)  # Field name made lowercase.
    totalmilkvalue = models.DecimalField(db_column='totalMilkValue', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    earningamt = models.DecimalField(db_column='earningAmt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    deductamt = models.DecimalField(db_column='deductAmt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    netamount = models.DecimalField(db_column='netAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    roundamount = models.DecimalField(db_column='roundAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cusercode = models.BigIntegerField(db_column='cUserCode', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    musercode = models.BigIntegerField(db_column='mUserCode', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    carryforwardamount = models.DecimalField(db_column='carryForwardAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalmilkqty = models.DecimalField(db_column='totalMilkQty', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblCycleSum'


class Tbldpuregister(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    sr_no = models.CharField(db_column='SR_No', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    imei_no = models.CharField(db_column='IMEI_No', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sim_no = models.CharField(db_column='SIM_No', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='RouteCode', blank=True, null=True)  # Field name made lowercase.
    mcccode = models.BigIntegerField(db_column='MCCCode', blank=True, null=True)  # Field name made lowercase.
    plantcode = models.BigIntegerField(db_column='PlantCode', blank=True, null=True)  # Field name made lowercase.
    dpuid = models.BigIntegerField(db_column='DPUId')  # Field name made lowercase.
    plant_other_code = models.CharField(db_column='Plant_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcc_other_code = models.CharField(db_column='Mcc_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmc_other_code = models.CharField(db_column='Bmc_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    route_other_code = models.CharField(db_column='Route_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='Mpp_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDPURegister'


class Tbldeductiondetails(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    deductioncode = models.ForeignKey('Tbldeductionheader', models.DO_NOTHING, db_column='DeductionCode', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.BigIntegerField(db_column='ItemCode', blank=True, null=True)  # Field name made lowercase.
    qty = models.DecimalField(db_column='Qty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gstrate = models.DecimalField(db_column='GstRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    grossamount = models.DecimalField(db_column='GrossAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gstamount = models.DecimalField(db_column='GstAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    netamount = models.DecimalField(db_column='NetAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdata = models.DateTimeField(db_column='CData', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mcdata = models.DateTimeField(db_column='MCData', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDeductionDetails'


class Tbldeductionheader(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    deductioncode = models.BigIntegerField(db_column='DeductionCode')  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    deductiondate = models.DateField(db_column='DeductionDate', blank=True, null=True)  # Field name made lowercase.
    grossamount = models.DecimalField(db_column='GrossAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    gstamount = models.DecimalField(db_column='GstAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    netamount = models.DecimalField(db_column='NetAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdata = models.DateTimeField(db_column='CData', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mcdata = models.DateTimeField(db_column='MCData', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDeductionHeader'


class Tbldeductiontype(models.Model):
    deductiontypeid = models.BigIntegerField(db_column='deductionTypeId', primary_key=True)  # Field name made lowercase.
    deductiontypedesc = models.CharField(db_column='deductionTypeDesc', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDeductionType'


class Tbldesktopsyncupdate(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    updateid = models.BigIntegerField(db_column='updateId')  # Field name made lowercase.
    updatefilename = models.CharField(db_column='updateFileName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    majorversion = models.IntegerField(db_column='majorVersion', blank=True, null=True)  # Field name made lowercase.
    minorversion = models.IntegerField(db_column='minorVersion', blank=True, null=True)  # Field name made lowercase.
    revisionversion = models.IntegerField(db_column='revisionVersion', blank=True, null=True)  # Field name made lowercase.
    updateurl = models.CharField(db_column='updateUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    updatetype = models.IntegerField(db_column='updateType', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDatetime', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    updatearchitecture = models.CharField(db_column='updateArchitecture', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    updateversion = models.CharField(db_column='updateVersion', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDesktopSyncUpdate'


class Tbldispatch(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dispatchdate = models.DateField(db_column='dispatchDate', blank=True, null=True)  # Field name made lowercase.
    dispatchtime = models.TimeField(db_column='dispatchTime', blank=True, null=True)  # Field name made lowercase.
    totalsamples = models.IntegerField(db_column='totalSamples', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    grade = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    lastsynchronized = models.DateTimeField(db_column='lastSynchronized', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    can = models.IntegerField(blank=True, null=True)
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='isApproved', blank=True, null=True)  # Field name made lowercase.
    isrejected = models.BooleanField(db_column='isRejected', blank=True, null=True)  # Field name made lowercase.
    publicip = models.CharField(db_column='PublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmc_other_code = models.CharField(db_column='BMC_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    syncstatus = models.CharField(db_column='SyncStatus', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    synctime = models.DateTimeField(db_column='SyncTime', blank=True, null=True)  # Field name made lowercase.
    analyzercode = models.BigIntegerField(db_column='analyzerCode', blank=True, null=True)  # Field name made lowercase.
    analyzerstring = models.CharField(db_column='analyzerString', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDispatch'


class Tbldispatchlog(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dispatchdate = models.DateField(db_column='dispatchDate', blank=True, null=True)  # Field name made lowercase.
    dispatchtime = models.TimeField(db_column='dispatchTime', blank=True, null=True)  # Field name made lowercase.
    totalsamples = models.IntegerField(db_column='totalSamples', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    grade = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    rejectedremark = models.CharField(db_column='RejectedRemark', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    can = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblDispatchLog'


class Tbldistrict(models.Model):
    dstcode = models.IntegerField(db_column='dstCode', primary_key=True)  # Field name made lowercase.
    dstname = models.CharField(db_column='dstName', max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDistrict'


class Tbldistrict1(models.Model):
    stcode = models.CharField(db_column='STCode', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    dtcode = models.CharField(db_column='DTCode', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    dtname = models.CharField(db_column='DTName', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sdtcode = models.CharField(db_column='SDTCode', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sdtname = models.CharField(db_column='SDTName', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    tvcode = models.CharField(db_column='TVCode', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    f8 = models.CharField(db_column='F8', max_length=255, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDistrict_1'


class Tbldockhistory(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId')  # Field name made lowercase.
    soccode = models.BigIntegerField(blank=True, null=True)
    socname = models.CharField(max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rcans = models.IntegerField(db_column='rCans', blank=True, null=True)  # Field name made lowercase.
    acans = models.IntegerField(db_column='aCans', blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo', blank=True, null=True)  # Field name made lowercase.
    did = models.IntegerField(db_column='DId', blank=True, null=True)  # Field name made lowercase.
    newsoccode = models.BigIntegerField(blank=True, null=True)
    newsocname = models.CharField(max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    newtype = models.CharField(db_column='newType', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    newgrade = models.CharField(db_column='newGrade', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    newcategory = models.IntegerField(db_column='newCategory', blank=True, null=True)  # Field name made lowercase.
    newweight = models.DecimalField(db_column='newWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    newrcans = models.IntegerField(db_column='newrCans', blank=True, null=True)  # Field name made lowercase.
    newacans = models.IntegerField(db_column='newaCans', blank=True, null=True)  # Field name made lowercase.
    newdid = models.IntegerField(db_column='newDId', blank=True, null=True)  # Field name made lowercase.
    collectioncode = models.IntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.IntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateField(blank=True, null=True)
    mtime = models.TimeField(blank=True, null=True)
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    history = models.IntegerField(db_column='History', blank=True, null=True)  # Field name made lowercase.
    weightrejected = models.DecimalField(db_column='WeightRejected', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    newweightrejected = models.DecimalField(db_column='newWeightRejected', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    oldpublicip = models.CharField(db_column='OldPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    newpublicip = models.CharField(db_column='NewPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    societyothercode = models.CharField(db_column='SocietyOtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    oldsocietyothercode = models.CharField(db_column='OldSocietyOtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='AutoID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDockHistory'


class Tbldockupdatelog(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    logid = models.BigIntegerField(db_column='LogId')  # Field name made lowercase.
    dumpdate = models.DateField(db_column='DumpDate', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='CenterCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    usercode = models.BigIntegerField(db_column='UserCode', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    publicip = models.CharField(db_column='PublicIp', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDockUpdateLog'


class Tbldpufirmware(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    updatecode = models.BigIntegerField(db_column='updateCode')  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    filename = models.CharField(db_column='fileName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ipaddress = models.CharField(db_column='ipAddress', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    filecontent = models.TextField(db_column='fileContent', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    filesize = models.CharField(db_column='fileSize', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    filechecksum = models.CharField(db_column='fileChecksum', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDpuFirmware'


class TbldpufirmwareMapping(models.Model):
    rowid = models.AutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    updatecode = models.BigIntegerField(db_column='updateCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloadtimestamp = models.DateTimeField(db_column='downloadTimestamp', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDpuFirmware_Mapping'


class Tbldpuratemanager(models.Model):
    rowid = models.AutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode')  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='CompanyId')  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='MCCId')  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='PlantId')  # Field name made lowercase.
    centerid = models.BigIntegerField(db_column='CenterId')  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='RouteId')  # Field name made lowercase.
    ratecode = models.BigIntegerField(db_column='RateCode')  # Field name made lowercase.
    ratetype = models.BigIntegerField(db_column='RateType')  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate')  # Field name made lowercase.
    effectiveshift = models.CharField(db_column='EffectiveShift', max_length=5, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=5, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=5, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    dpucommand = models.CharField(db_column='DpuCommand', max_length=5, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    isdownloaded = models.BooleanField(db_column='IsDownloaded')  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='Cid')  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate')  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='Mid')  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate')  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDpuRateManager'


class Tbldpusettings(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    configurationcode = models.BigIntegerField(db_column='ConfigurationCode')  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    filename = models.CharField(db_column='fileName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    filecontent = models.TextField(db_column='fileContent', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ipaddress = models.CharField(db_column='ipAddress', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    filesize = models.CharField(db_column='fileSize', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDpuSettings'


class TbldpusettingsMapping(models.Model):
    rowid = models.AutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    configurationcode = models.BigIntegerField(db_column='ConfigurationCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloadtimestamp = models.DateTimeField(db_column='downloadTimestamp', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblDpuSettings_Mapping'


class Tblearningdeductiondefinition(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    eddefinitioncode = models.BigIntegerField(db_column='edDefinitionCode')  # Field name made lowercase.
    edheadcode = models.BigIntegerField(db_column='edHeadCode')  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    isonqty = models.BooleanField(db_column='isOnQty', blank=True, null=True)  # Field name made lowercase.
    isonpercentage = models.BooleanField(db_column='isOnPercentage', blank=True, null=True)  # Field name made lowercase.
    value = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='cDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='mDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEarningDeductionDefinition'


class Tblearningdeductionhead(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    edheadcode = models.BigIntegerField(db_column='edHeadCode')  # Field name made lowercase.
    edheaddesc = models.CharField(db_column='edHeadDesc', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    iscredit = models.BooleanField(db_column='isCredit', blank=True, null=True)  # Field name made lowercase.
    priority = models.IntegerField(blank=True, null=True)
    gst = models.IntegerField(blank=True, null=True)
    isedforfarmer = models.BooleanField(db_column='isEdForFarmer', blank=True, null=True)  # Field name made lowercase.
    isedforsociety = models.BooleanField(db_column='isEdForSociety', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='cDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='mDate', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='effectiveDate')  # Field name made lowercase.
    isonqty = models.BooleanField(db_column='isOnQty')  # Field name made lowercase.
    isonpercentage = models.BooleanField(db_column='isOnPercentage')  # Field name made lowercase.
    value = models.DecimalField(max_digits=18, decimal_places=3)
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEarningDeductionHead'


class Tbleddefinitionmapping(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    eddefmappingid = models.BigIntegerField(db_column='edDefMappingId', )  # Field name made lowercase.
    eddefinitioncode = models.BigIntegerField(db_column='edDefinitionCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='cDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='mDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEdDefinitionMapping'


class Tbledheadmapping(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    eddefmappingid = models.BigIntegerField(db_column='edDefMappingId')  # Field name made lowercase.
    edheadcode = models.BigIntegerField(db_column='edHeadCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='cDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='mDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEdHeadMapping'


class Tbledvoucher(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    voucherid = models.BigIntegerField(db_column='voucherId')  # Field name made lowercase.
    processdate = models.DateField(db_column='processDate', blank=True, null=True)  # Field name made lowercase.
    cycleid = models.BigIntegerField(db_column='cycleId', blank=True, null=True)  # Field name made lowercase.
    cycleno = models.IntegerField(db_column='cycleNo', blank=True, null=True)  # Field name made lowercase.
    companycode = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='companyCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode', blank=True, null=True)  # Field name made lowercase.
    edheadcode = models.ForeignKey(Tblearningdeductionhead, models.DO_NOTHING, db_column='edHeadCode', blank=True, null=True)  # Field name made lowercase.
    edheaddesc = models.CharField(db_column='edHeadDesc', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    edamount = models.DecimalField(db_column='edAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iscredit = models.BooleanField(db_column='isCredit', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    cid = models.BigIntegerField(db_column='cId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='cDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='mId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='mDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblEdVoucher'


class Tblerrorinfo(models.Model):
    errorid = models.AutoField(db_column='ErrorId', primary_key=True)  # Field name made lowercase.
    errornumber = models.TextField(db_column='ErrorNumber', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorseverity = models.TextField(db_column='ErrorSeverity', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorstate = models.TextField(db_column='ErrorState', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorprocedure = models.TextField(db_column='ErrorProcedure', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errorline = models.TextField(db_column='ErrorLine', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errormessage = models.TextField(db_column='ErrorMessage', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    errordate = models.DateTimeField(db_column='ErrorDate', blank=True, null=True)  # Field name made lowercase.
    crid = models.BigIntegerField(db_column='CrID', blank=True, null=True)  # Field name made lowercase.
    crdate = models.DateTimeField(db_column='CrDate', blank=True, null=True)  # Field name made lowercase.
    mdid = models.BigIntegerField(db_column='MdID', blank=True, null=True)  # Field name made lowercase.
    mddate = models.DateTimeField(db_column='MdDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblErrorInfo'


class Tblfarmer(models.Model):
    farmerid = models.BigIntegerField(db_column='farmerId',primary_key=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    middlename = models.CharField(db_column='middleName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    birthdate = models.DateField(db_column='birthDate', blank=True, null=True)  # Field name made lowercase.
    caste = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.ForeignKey('Tblmcc',on_delete=models.SET_NULL,db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmercode = models.CharField(db_column='farmerCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.BigIntegerField(db_column='bankCode', blank=True, null=True)  # Field name made lowercase.
    bankbranchname = models.CharField(db_column='bankBranchName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountname = models.CharField(db_column='accountName', max_length=150, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsccode = models.CharField(db_column='ifscCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountnumber = models.CharField(db_column='accountNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pannumber = models.CharField(db_column='panNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    beneficiaryname = models.CharField(db_column='beneficiaryName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    adharnumber = models.CharField(db_column='adharNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    expirydate = models.DateField(db_column='expiryDate', blank=True, null=True)  # Field name made lowercase.
    expiryshift = models.CharField(db_column='expiryShift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='routeCode', blank=True, null=True)  # Field name made lowercase.
    formnumber = models.CharField(db_column='FormNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fathername = models.CharField(db_column='FatherName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    qualification = models.CharField(db_column='Qualification', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    postoffice = models.CharField(db_column='PostOffice', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cowheriferno = models.IntegerField(db_column='CowHeriferNo', blank=True, null=True)  # Field name made lowercase.
    buffaloheriferno = models.IntegerField(db_column='BuffaloHeriferNo', blank=True, null=True)  # Field name made lowercase.
    mixheriferno = models.IntegerField(db_column='MixHeriferNo', blank=True, null=True)  # Field name made lowercase.
    desicowheriferno = models.IntegerField(db_column='DesiCowHeriferNo', blank=True, null=True)  # Field name made lowercase.
    crossbredheriferno = models.IntegerField(db_column='CrossbredHeriferNo', blank=True, null=True)  # Field name made lowercase.
    cowdryno = models.IntegerField(db_column='CowDryNo', blank=True, null=True)  # Field name made lowercase.
    buffalodryno = models.IntegerField(db_column='BuffaloDryNo', blank=True, null=True)  # Field name made lowercase.
    mixdryno = models.IntegerField(db_column='MixDryNo', blank=True, null=True)  # Field name made lowercase.
    desicowdryno = models.IntegerField(db_column='DesiCowDryNo', blank=True, null=True)  # Field name made lowercase.
    crossbreddryno = models.IntegerField(db_column='CrossbredDryNo', blank=True, null=True)  # Field name made lowercase.
    cowanimalnos = models.IntegerField(db_column='CowAnimalNos', blank=True, null=True)  # Field name made lowercase.
    buffaloanimalnos = models.IntegerField(db_column='BuffaloAnimalNos', blank=True, null=True)  # Field name made lowercase.
    mixanimalnos = models.IntegerField(db_column='MixAnimalNos', blank=True, null=True)  # Field name made lowercase.
    desicowanimalnos = models.IntegerField(db_column='DesiCowAnimalNos', blank=True, null=True)  # Field name made lowercase.
    crossbredanimalnos = models.IntegerField(db_column='CrossbredAnimalNos', blank=True, null=True)  # Field name made lowercase.
    lpdno = models.IntegerField(db_column='LpdNo', blank=True, null=True)  # Field name made lowercase.
    householdconsumption = models.IntegerField(db_column='HouseholdConsumption', blank=True, null=True)  # Field name made lowercase.
    marketconsumption = models.IntegerField(db_column='MarketConsumption', blank=True, null=True)  # Field name made lowercase.
    particluar1name = models.CharField(db_column='Particluar1Name', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    particluar1gender = models.CharField(db_column='Particluar1Gender', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    particluar1age = models.IntegerField(db_column='Particluar1Age', blank=True, null=True)  # Field name made lowercase.
    particluar1relation = models.CharField(db_column='Particluar1Relation', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    nomineename = models.CharField(db_column='NomineeName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    relation = models.CharField(db_column='Relation', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    nomineeaddress = models.CharField(db_column='NomineeAddress', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    guardianname = models.CharField(db_column='GuardianName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    memberfamilyage = models.IntegerField(db_column='MemberFamilyAge', blank=True, null=True)  # Field name made lowercase.
    admissionfee = models.DecimalField(db_column='AdmissionFee', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shareqty = models.DecimalField(db_column='ShareQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paidamount = models.DecimalField(db_column='PaidAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    depositorbankname = models.CharField(db_column='DepositorBankName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    depositorbranchname = models.CharField(db_column='DepositorBranchName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ddno = models.CharField(db_column='DDNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    transactiondate = models.CharField(db_column='TransactionDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    wefdate = models.CharField(db_column='WefDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    uniquemembercode = models.CharField(db_column='UniqueMemberCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    membertype = models.CharField(db_column='MemberType', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    approvalstatus = models.CharField(db_column='ApprovalStatus', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    acceptedby = models.CharField(db_column='AcceptedBy', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    approvaldate = models.CharField(db_column='ApprovalDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(blank=True, null=True)
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otp = models.CharField(db_column='OTP', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isotpexpired = models.BooleanField(db_column='isOTPExpired', blank=True, null=True)  # Field name made lowercase.
    otpdatetimeist = models.DateTimeField(db_column='OTPDateTimeIST', blank=True, null=True)  # Field name made lowercase.
    img = models.TextField(db_column='Img', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    defaultmilktype = models.CharField(db_column='defaultMilkType', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    
    def __str__(self):
        if self.firstname :
            return f'{self.firstname} ({self.farmerid})'
        else:
            return f'{self.farmercode} ({self.farmerid})'
    
    
    class Meta:
        managed = False
        db_table = 'tblFarmer'


class Tblfarmercollection(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.TimeField(db_column='dumpTime', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.ForeignKey(Tblfarmer,on_delete=models.CASCADE,db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    # farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    lastsynchronized = models.DateTimeField(db_column='lastSynchronized', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='isApproved', blank=True, null=True)  # Field name made lowercase.
    isrejected = models.BooleanField(db_column='isRejected', blank=True, null=True)  # Field name made lowercase.
    fkfarmerid = models.BigIntegerField(db_column='fkFarmerId', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    publicip = models.CharField(db_column='PublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isratecalculate = models.BooleanField(db_column='IsRateCalculate', blank=True, null=True)  # Field name made lowercase.
    ratecalculate = models.DateTimeField(db_column='RateCalculate', blank=True, null=True)  # Field name made lowercase.
    bmc_other_code = models.CharField(db_column='BMC_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    syncstatus = models.CharField(db_column='SyncStatus', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    synctime = models.DateTimeField(db_column='SyncTime', blank=True, null=True)  # Field name made lowercase.
    member_other_code = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    analyzercode = models.BigIntegerField(db_column='analyzerCode', blank=True, null=True)  # Field name made lowercase.
    analyzerstring = models.CharField(db_column='analyzerString', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    commissionperunit = models.DecimalField(db_column='CommissionPerUnit', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    commissionamount = models.DecimalField(db_column='CommissionAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ispaymentdone = models.BooleanField(db_column='IsPaymentDone', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFarmerCollection'


class Tblfarmercollection2(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.TimeField(db_column='dumpTime', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    lastsynchronized = models.DateTimeField(db_column='lastSynchronized', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='isApproved', blank=True, null=True)  # Field name made lowercase.
    isrejected = models.BooleanField(db_column='isRejected', blank=True, null=True)  # Field name made lowercase.
    fkfarmerid = models.BigIntegerField(db_column='fkFarmerId', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    publicip = models.CharField(db_column='PublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isratecalculate = models.BooleanField(db_column='IsRateCalculate', blank=True, null=True)  # Field name made lowercase.
    ratecalculate = models.DateTimeField(db_column='RateCalculate', blank=True, null=True)  # Field name made lowercase.
    bmc_other_code = models.CharField(db_column='BMC_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    syncstatus = models.CharField(db_column='SyncStatus', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    synctime = models.DateTimeField(db_column='SyncTime', blank=True, null=True)  # Field name made lowercase.
    member_other_code = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblFarmerCollection2'


class Tblfarmercollectionapprovelog(models.Model):
    rowid = models.DecimalField(db_column='rowId',primary_key=True, max_digits=20, decimal_places=0)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    fkfarmerid = models.BigIntegerField(db_column='fkFarmerId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=3, db_collation='Latin1_General_CI_AI')
    logdatetime = models.DateTimeField(db_column='logDateTime', blank=True, null=True)  # Field name made lowercase.
    operation = models.CharField(max_length=25, db_collation='Latin1_General_CI_AI', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblFarmerCollectionApproveLog'


class Tblfarmercollectionlog(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.TimeField(db_column='dumpTime', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rejectionremark = models.TextField(db_column='RejectionRemark', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fkfarmerid = models.BigIntegerField(db_column='fkFarmerId', blank=True, null=True)  # Field name made lowercase.
    societyothercode = models.CharField(db_column='SocietyOtherCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFarmerCollectionLog'


class Tblfarmercollectionsms(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.TimeField(db_column='dumpTime', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='routeId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    lastsynchronized = models.DateTimeField(db_column='lastSynchronized', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='isApproved', blank=True, null=True)  # Field name made lowercase.
    isrejected = models.BooleanField(db_column='isRejected', blank=True, null=True)  # Field name made lowercase.
    fkfarmerid = models.BigIntegerField(db_column='fkFarmerId', blank=True, null=True)  # Field name made lowercase.
    smstype = models.CharField(db_column='SMSType', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    messagestring = models.TextField(db_column='messageString', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    messageresponse = models.TextField(db_column='messageResponse', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFarmerCollectionSMS'


class Tblfarmercollectionstaging(models.Model):
    rowid = models.BigAutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='dumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.TimeField(db_column='dumpTime', blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='sampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmerid = models.BigIntegerField(db_column='farmerId', blank=True, null=True)  # Field name made lowercase.
    plantcode = models.BigIntegerField(db_column='plantCode', blank=True, null=True)  # Field name made lowercase.
    mcccode = models.BigIntegerField(db_column='mccCode', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='centerCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='routeCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='societyCode', blank=True, null=True)  # Field name made lowercase.
    deviceid = models.CharField(db_column='deviceId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    weight = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    weightliter = models.DecimalField(db_column='weightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    water = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    rtpl = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    totalamount = models.DecimalField(db_column='totalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    qtytime = models.DateTimeField(blank=True, null=True)
    qltytime = models.DateTimeField(blank=True, null=True)
    kgltrconst = models.DecimalField(db_column='kgLtrConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    ltrkgconst = models.DecimalField(db_column='ltrKgConst', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    qtymode = models.CharField(db_column='qtyMode', max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isapproved = models.BooleanField(db_column='isApproved', blank=True, null=True)  # Field name made lowercase.
    isrejected = models.BooleanField(db_column='isRejected', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    eventaction = models.IntegerField(db_column='eventAction', blank=True, null=True)  # Field name made lowercase.
    uploaddatetime = models.DateTimeField(db_column='uploadDatetime', blank=True, null=True)  # Field name made lowercase.
    isprocessed = models.BooleanField(db_column='isProcessed', blank=True, null=True)  # Field name made lowercase.
    analyzercode = models.BigIntegerField(db_column='analyzerCode', blank=True, null=True)  # Field name made lowercase.
    analyzerstring = models.CharField(db_column='analyzerString', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    processeddatetime = models.DateTimeField(db_column='processedDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFarmerCollectionStaging'


class Tblfarmerhistory(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    farmerid = models.BigIntegerField(db_column='farmerId')  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    middlename = models.CharField(db_column='middleName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    birthdate = models.DateField(db_column='birthDate', blank=True, null=True)  # Field name made lowercase.
    caste = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    soccode = models.BigIntegerField(db_column='socCode', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmercode = models.CharField(db_column='farmerCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.IntegerField(db_column='bankCode', blank=True, null=True)  # Field name made lowercase.
    bankbranchname = models.CharField(db_column='bankBranchName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountname = models.CharField(db_column='accountName', max_length=150, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsccode = models.CharField(db_column='ifscCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountnumber = models.CharField(db_column='accountNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pannumber = models.CharField(db_column='panNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    beneficiaryname = models.CharField(db_column='beneficiaryName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    adharnumber = models.CharField(db_column='adharNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    expirydate = models.DateField(db_column='expiryDate', blank=True, null=True)  # Field name made lowercase.
    expiryshift = models.CharField(db_column='expiryShift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='cntCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='routeCode', blank=True, null=True)  # Field name made lowercase.
    formnumber = models.CharField(db_column='FormNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fathername = models.CharField(db_column='FatherName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    qualification = models.CharField(db_column='Qualification', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    postoffice = models.CharField(db_column='PostOffice', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cowheriferno = models.IntegerField(db_column='CowHeriferNo', blank=True, null=True)  # Field name made lowercase.
    buffaloheriferno = models.IntegerField(db_column='BuffaloHeriferNo', blank=True, null=True)  # Field name made lowercase.
    mixheriferno = models.IntegerField(db_column='MixHeriferNo', blank=True, null=True)  # Field name made lowercase.
    desicowheriferno = models.IntegerField(db_column='DesiCowHeriferNo', blank=True, null=True)  # Field name made lowercase.
    crossbredheriferno = models.IntegerField(db_column='CrossbredHeriferNo', blank=True, null=True)  # Field name made lowercase.
    cowdryno = models.IntegerField(db_column='CowDryNo', blank=True, null=True)  # Field name made lowercase.
    buffalodryno = models.IntegerField(db_column='BuffaloDryNo', blank=True, null=True)  # Field name made lowercase.
    mixdryno = models.IntegerField(db_column='MixDryNo', blank=True, null=True)  # Field name made lowercase.
    desicowdryno = models.IntegerField(db_column='DesiCowDryNo', blank=True, null=True)  # Field name made lowercase.
    crossbreddryno = models.IntegerField(db_column='CrossbredDryNo', blank=True, null=True)  # Field name made lowercase.
    cowanimalnos = models.IntegerField(db_column='CowAnimalNos', blank=True, null=True)  # Field name made lowercase.
    buffaloanimalnos = models.IntegerField(db_column='BuffaloAnimalNos', blank=True, null=True)  # Field name made lowercase.
    mixanimalnos = models.IntegerField(db_column='MixAnimalNos', blank=True, null=True)  # Field name made lowercase.
    desicowanimalnos = models.IntegerField(db_column='DesiCowAnimalNos', blank=True, null=True)  # Field name made lowercase.
    crossbredanimalnos = models.IntegerField(db_column='CrossbredAnimalNos', blank=True, null=True)  # Field name made lowercase.
    lpdno = models.IntegerField(db_column='LpdNo', blank=True, null=True)  # Field name made lowercase.
    householdconsumption = models.IntegerField(db_column='HouseholdConsumption', blank=True, null=True)  # Field name made lowercase.
    marketconsumption = models.IntegerField(db_column='MarketConsumption', blank=True, null=True)  # Field name made lowercase.
    particluar1name = models.CharField(db_column='Particluar1Name', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    particluar1gender = models.CharField(db_column='Particluar1Gender', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    particluar1age = models.IntegerField(db_column='Particluar1Age', blank=True, null=True)  # Field name made lowercase.
    particluar1relation = models.CharField(db_column='Particluar1Relation', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    nomineename = models.CharField(db_column='NomineeName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    relation = models.CharField(db_column='Relation', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    nomineeaddress = models.CharField(db_column='NomineeAddress', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    guardianname = models.CharField(db_column='GuardianName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    memberfamilyage = models.IntegerField(db_column='MemberFamilyAge', blank=True, null=True)  # Field name made lowercase.
    admissionfee = models.DecimalField(db_column='AdmissionFee', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shareqty = models.DecimalField(db_column='ShareQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paidamount = models.DecimalField(db_column='PaidAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    depositorbankname = models.CharField(db_column='DepositorBankName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    depositorbranchname = models.CharField(db_column='DepositorBranchName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ddno = models.CharField(db_column='DDNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    transactiondate = models.CharField(db_column='TransactionDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    wefdate = models.CharField(db_column='WefDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    uniquemembercode = models.CharField(db_column='UniqueMemberCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    membertype = models.CharField(db_column='MemberType', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    approvalstatus = models.CharField(db_column='ApprovalStatus', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    acceptedby = models.CharField(db_column='AcceptedBy', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    approvaldate = models.CharField(db_column='ApprovalDate', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='HistoryTimeStamp', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='HistoryCreatedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblFarmerHistory'


class Tblgovernmentcommission(models.Model):
    commissionid = models.BigIntegerField(db_column='CommissionId', primary_key=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    valueperqty = models.DecimalField(db_column='ValuePerQty', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='CompanyId', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateField(db_column='cDatetime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblGovernmentCommission'


class Tblhamlet(models.Model):
    hamletid = models.BigIntegerField(db_column='HamletId', primary_key=True)  # Field name made lowercase.
    hamletname = models.CharField(db_column='HamletName', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    villageid = models.IntegerField(db_column='VillageId', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblHamlet'


class Tbllabhistory(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId')  # Field name made lowercase.
    soccode = models.BigIntegerField(blank=True, null=True)
    socname = models.CharField(max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    snf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    lid = models.IntegerField(db_column='LId', blank=True, null=True)  # Field name made lowercase.
    newfat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    newlr = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    newsnf = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    newlid = models.IntegerField(db_column='newLId', blank=True, null=True)  # Field name made lowercase.
    companycode = models.IntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    collectioncode = models.IntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateField(blank=True, null=True)
    mtime = models.TimeField(blank=True, null=True)
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    history = models.IntegerField(db_column='History', blank=True, null=True)  # Field name made lowercase.
    oldpublicip = models.CharField(db_column='OldPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    newpublicip = models.CharField(db_column='NewPublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='AutoID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLabHistory'


class Tblloginhistory(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    usercode = models.IntegerField(db_column='UserCode')  # Field name made lowercase.
    logindatetime = models.DateTimeField(db_column='LoginDatetime', blank=True, null=True)  # Field name made lowercase.
    publicip = models.TextField(db_column='PublicIp', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblLoginHistory'


class Tblmcc(models.Model):
    mccid = models.BigIntegerField(db_column='mccId',primary_key=True)  # Field name made lowercase.
    mccname = models.CharField(db_column='mccName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateField(db_column='validFrom', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='contactPerson', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcccode = models.CharField(db_column='mccCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gstnumber = models.CharField(db_column='gstNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    
    def __str__(self):
        return f'{self.mccname} ({self.mccid})'
    
    class Meta:
        managed = False
        db_table = 'tblMCC'


class Tblmcchistory(models.Model):
    mccid = models.BigIntegerField(db_column='mccId',primary_key=True)  # Field name made lowercase.
    mccname = models.CharField(db_column='mccName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    validfrom = models.DateField(db_column='validFrom', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    companyid = models.ForeignKey('Tblmstcompany', models.DO_NOTHING, db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='contactPerson', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcccode = models.CharField(db_column='mccCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gstnumber = models.CharField(db_column='gstNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='HistoryTimeStamp', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='HistoryCreatedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMCCHistory'


class Tblmmilk(models.Model):
    rawid = models.DecimalField(db_column='RawId',primary_key=True, max_digits=30, decimal_places=0)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase. The composite primary key (DumpDate, Shift, rtCode, soccode, Grade, DockNo, cntcode, CollectionCode, CompanyCode) found, that is not supported. The first column is selected.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    soccode = models.BigIntegerField()
    socname = models.CharField(db_column='socName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='rtCode')  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    bweight = models.DecimalField(db_column='BWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bweightltr = models.DecimalField(db_column='BWeightLtr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bfat = models.DecimalField(db_column='BFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bclr = models.DecimalField(db_column='BCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bsnf = models.DecimalField(db_column='BSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bprotein = models.DecimalField(db_column='BProtein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    blactose = models.DecimalField(db_column='BLactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cweight = models.DecimalField(db_column='CWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cweightltr = models.DecimalField(db_column='CWeightlTR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfat = models.DecimalField(db_column='CFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cclr = models.DecimalField(db_column='CCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    csnf = models.DecimalField(db_column='CSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cprotein = models.DecimalField(db_column='CProtein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    clactose = models.DecimalField(db_column='CLactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mweight = models.DecimalField(db_column='mWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mweightltr = models.DecimalField(db_column='MWeightlTR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mfat = models.DecimalField(db_column='mFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mclr = models.DecimalField(db_column='MCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    msnf = models.DecimalField(db_column='mSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mprotein = models.DecimalField(db_column='MProtein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mlactose = models.DecimalField(db_column='MLactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bsno = models.IntegerField(db_column='BSno', blank=True, null=True)  # Field name made lowercase.
    csno = models.IntegerField(db_column='CSno', blank=True, null=True)  # Field name made lowercase.
    msno = models.IntegerField(db_column='mSno', blank=True, null=True)  # Field name made lowercase.
    bacans = models.IntegerField(db_column='BACans', blank=True, null=True)  # Field name made lowercase.
    cacans = models.IntegerField(db_column='CACans', blank=True, null=True)  # Field name made lowercase.
    macans = models.IntegerField(db_column='MACans', blank=True, null=True)  # Field name made lowercase.
    brcans = models.IntegerField(db_column='BRCans', blank=True, null=True)  # Field name made lowercase.
    crcans = models.IntegerField(db_column='CRCans', blank=True, null=True)  # Field name made lowercase.
    mrcans = models.IntegerField(db_column='MrCans', blank=True, null=True)  # Field name made lowercase.
    crate = models.DecimalField(db_column='cRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    brate = models.DecimalField(db_column='bRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mrate = models.DecimalField(db_column='mRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cpayment = models.DecimalField(db_column='cPayment', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    bpayment = models.DecimalField(db_column='bPayment', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    mpayment = models.DecimalField(db_column='mPayment', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    bkgfat = models.DecimalField(db_column='BKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bkgsnf = models.DecimalField(db_column='BKGSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ckgfat = models.DecimalField(db_column='CKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ckgsnf = models.DecimalField(db_column='CKGSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mkgfat = models.DecimalField(db_column='MKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mkgsnf = models.DecimalField(db_column='MKGsnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField()
    collectioncode = models.IntegerField(db_column='CollectionCode')  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode')  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    sampleid = models.IntegerField(db_column='SampleId', blank=True, null=True)  # Field name made lowercase.
    bamount = models.DecimalField(db_column='BAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bufrate = models.DecimalField(db_column='BufRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cowrate = models.DecimalField(db_column='CowRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mamount = models.DecimalField(db_column='MAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    issms = models.BooleanField(db_column='IsSMS', blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo')  # Field name made lowercase.
    bsampleno = models.DecimalField(db_column='BSampleNo', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bdensity = models.DecimalField(db_column='BDensity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bfreezingpoint = models.DecimalField(db_column='BFreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    btime = models.TimeField(db_column='BTime', blank=True, null=True)  # Field name made lowercase.
    bdate = models.DateTimeField(db_column='BDate', blank=True, null=True)  # Field name made lowercase.
    bwater = models.CharField(db_column='BWater', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    burea = models.CharField(db_column='BUrea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmaltodex = models.CharField(db_column='BMaltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bammsulp = models.CharField(db_column='BAmmsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bsucrose = models.CharField(db_column='BSucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    babnormal = models.CharField(db_column='BAbnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bbadsample = models.CharField(db_column='BBadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    csampleno = models.DecimalField(db_column='CSampleNo', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cdensity = models.DecimalField(db_column='CDensity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfreezingpoint = models.DecimalField(db_column='CFreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ctime = models.TimeField(db_column='CTime', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    cwater = models.CharField(db_column='CWater', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    curea = models.CharField(db_column='CUrea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cmaltodex = models.CharField(db_column='CMaltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cammsulp = models.CharField(db_column='CAmmsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    csucrose = models.CharField(db_column='CSucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cabnormal = models.CharField(db_column='CAbnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cbadsample = models.CharField(db_column='CBadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    msampleno = models.DecimalField(db_column='MSampleNo', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mdensity = models.DecimalField(db_column='MDensity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mfreezingpoint = models.DecimalField(db_column='MFreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mtime = models.TimeField(db_column='MTime', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    mwater = models.CharField(db_column='MWater', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    murea = models.CharField(db_column='MUrea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mmaltodex = models.CharField(db_column='MMaltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mammsulp = models.CharField(db_column='MAmmsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    msucrose = models.CharField(db_column='MSucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mabnormal = models.CharField(db_column='MAbnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mbadsample = models.CharField(db_column='MBadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    publicip = models.CharField(db_column='PublicIp', max_length=256, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='MPP_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='AutoID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMMilk'
        unique_together = (('dumpdate', 'shift', 'rtcode', 'soccode', 'grade', 'dockno', 'cntcode', 'collectioncode', 'companycode'),)


class Tblmmilksms(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(blank=True, null=True)
    socname = models.CharField(db_column='socName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='rtCode', blank=True, null=True)  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    bweight = models.DecimalField(db_column='BWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bweightltr = models.DecimalField(db_column='BWeightLtr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bfat = models.DecimalField(db_column='BFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bclr = models.DecimalField(db_column='BCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bsnf = models.DecimalField(db_column='BSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cweight = models.DecimalField(db_column='CWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cweightltr = models.DecimalField(db_column='CWeightlTR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfat = models.DecimalField(db_column='CFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cclr = models.DecimalField(db_column='CCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    csnf = models.DecimalField(db_column='CSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mweight = models.DecimalField(db_column='mWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mweightltr = models.DecimalField(db_column='MWeightlTR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mfat = models.DecimalField(db_column='mFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mclr = models.DecimalField(db_column='MCLR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    msnf = models.DecimalField(db_column='mSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crate = models.DecimalField(db_column='cRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    brate = models.DecimalField(db_column='bRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mrate = models.DecimalField(db_column='mRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bkgfat = models.DecimalField(db_column='BKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bkgsnf = models.DecimalField(db_column='BKGSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ckgfat = models.DecimalField(db_column='CKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ckgsnf = models.DecimalField(db_column='CKGSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mkgfat = models.DecimalField(db_column='MKGFAT', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mkgsnf = models.DecimalField(db_column='MKGsnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(blank=True, null=True)
    collectioncode = models.BigIntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    bamount = models.DecimalField(db_column='BAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mamount = models.DecimalField(db_column='MAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo', blank=True, null=True)  # Field name made lowercase.
    smstype = models.CharField(db_column='SMSType', max_length=64, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    messagestring = models.CharField(db_column='MessageString', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    messageresponse = models.CharField(db_column='MessageResponse', max_length=8000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMMilkSMS'


class Tblmachine(models.Model):
    machinecode = models.BigIntegerField(db_column='machineCode', primary_key=True)  # Field name made lowercase.
    machinename = models.CharField(db_column='machineName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    machinetype = models.CharField(db_column='machineType', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    baudrate = models.CharField(db_column='baudRate', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fatstartindex = models.IntegerField(db_column='fatStartIndex', blank=True, null=True)  # Field name made lowercase.
    fatendindex = models.IntegerField(db_column='fatEndIndex', blank=True, null=True)  # Field name made lowercase.
    snfstartindex = models.IntegerField(db_column='snfStartIndex', blank=True, null=True)  # Field name made lowercase.
    snfendindex = models.IntegerField(db_column='snfEndIndex', blank=True, null=True)  # Field name made lowercase.
    clrstartindex = models.IntegerField(db_column='clrStartIndex', blank=True, null=True)  # Field name made lowercase.
    clrendindex = models.IntegerField(db_column='clrEndIndex', blank=True, null=True)  # Field name made lowercase.
    proteinstartindex = models.IntegerField(db_column='proteinStartIndex', blank=True, null=True)  # Field name made lowercase.
    proteinendindex = models.IntegerField(db_column='proteinEndIndex', blank=True, null=True)  # Field name made lowercase.
    weightstartindex = models.IntegerField(db_column='weightStartIndex', blank=True, null=True)  # Field name made lowercase.
    weightendindex = models.IntegerField(db_column='weightEndIndex', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    delimiter = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    ble = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    serial = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    interfacebox = models.CharField(db_column='interfaceBox', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    tarechar = models.CharField(db_column='tareChar', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdecimalthere = models.BooleanField(db_column='isDecimalThere', blank=True, null=True)  # Field name made lowercase.
    digitsafterdecimal = models.IntegerField(db_column='digitsAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    ble2 = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    iscommandenable = models.BooleanField(db_column='isCommandEnable', blank=True, null=True)  # Field name made lowercase.
    modelname = models.CharField(db_column='modelName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMachine'


class Tblmstbank(models.Model):
    bankcode = models.BigIntegerField(db_column='BankCode', primary_key=True)  # Field name made lowercase.
    bankname = models.CharField(db_column='BankName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bankhocode = models.CharField(db_column='BankHOCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bankifsccode = models.CharField(db_column='BankIFSCCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstBank'


class Tblmstcenter(models.Model):
    cntcode = models.IntegerField(db_column='cntCode',primary_key=True)  # Field name made lowercase.
    mcccode = models.IntegerField(db_column='MccCode', blank=True, null=True)  # Field name made lowercase.
    cntname = models.CharField(db_column='cntName', max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    comapnycode = models.IntegerField(db_column='ComapnyCode')  # Field name made lowercase.
    cntdocks = models.IntegerField(db_column='cntDocks', blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    add1 = models.CharField(db_column='Add1', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.IntegerField(db_column='PinCode', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isbowl = models.BooleanField(db_column='IsBowl', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.IntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.BigIntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstCenter'


class Tblmstcenterhistory(models.Model):
    cntcode = models.IntegerField(db_column='cntCode',primary_key=True)  # Field name made lowercase.
    mcccode = models.IntegerField(db_column='MccCode', blank=True, null=True)  # Field name made lowercase.
    cntname = models.CharField(db_column='cntName', max_length=35, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    comapnycode = models.IntegerField(db_column='ComapnyCode')  # Field name made lowercase.
    cntdocks = models.IntegerField(db_column='cntDocks', blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    add1 = models.CharField(db_column='Add1', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.IntegerField(db_column='PinCode', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isbowl = models.BooleanField(db_column='IsBowl', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.IntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.BigIntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='mccId', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='plantId', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='HistoryTimeStamp', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='HistoryCreatedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstCenterHistory'


class Tblmstcompany(models.Model):
    companycode = models.BigIntegerField(db_column='CompanyCode', primary_key=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyaddress = models.CharField(db_column='CompanyAddress', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='Pincode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mobileno = models.CharField(db_column='MobileNo', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailId', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.IntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    shortdescription = models.CharField(db_column='ShortDescription', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.BigIntegerField(db_column='bankCode', blank=True, null=True)  # Field name made lowercase.
    bankbranchname = models.CharField(db_column='bankBranchName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountname = models.CharField(db_column='accountName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsccode = models.CharField(db_column='ifscCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountnumber = models.CharField(db_column='accountNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstCompany'


class Tblmstcontractor(models.Model):
    rtccode = models.IntegerField(db_column='RtcCode', primary_key=True)  # Field name made lowercase.
    rtcname = models.CharField(db_column='RtcName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtcrate = models.FloatField(db_column='RtcRate', blank=True, null=True)  # Field name made lowercase.
    mobile = models.CharField(db_column='Mobile', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailId', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    birthdate = models.DateTimeField(db_column='BirthDate', blank=True, null=True)  # Field name made lowercase.
    add1 = models.CharField(db_column='Add1', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='PINCode', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.TextField(db_column='State', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    country = models.TextField(db_column='Country', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companycode = models.TextField(db_column='CompanyCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.ForeignKey(Tblcountry, models.DO_NOTHING, db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstContractor'


class Tblmstsupervisor(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    fscode = models.IntegerField(db_column='FsCode')  # Field name made lowercase.
    fsname = models.CharField(db_column='FsName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    designation = models.TextField(db_column='Designation', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mobile = models.CharField(db_column='Mobile', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailid = models.CharField(db_column='EmailId', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gender = models.TextField(db_column='Gender', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    birthdate = models.DateTimeField(db_column='BirthDate', blank=True, null=True)  # Field name made lowercase.
    add1 = models.TextField(db_column='Add1', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.IntegerField(db_column='PINCode', blank=True, null=True)  # Field name made lowercase.
    city = models.TextField(db_column='City', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.TextField(db_column='State', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    country = models.TextField(db_column='Country', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.TextField(db_column='CompanyCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstSupervisor'


class Tblmsttenker(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    vehicalcode = models.IntegerField(db_column='VehicalCode', blank=True, null=True)  # Field name made lowercase.
    vehicalname = models.CharField(db_column='VehicalName', max_length=40, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtccode = models.IntegerField(db_column='RtcCode', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    capacity = models.CharField(db_column='Capacity', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mobileno1 = models.CharField(db_column='MobileNo1', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    companycode = models.TextField(db_column='CompanyCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='Mid', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblMstTenker'


class Tblparentmenu(models.Model):
    parentid = models.IntegerField(db_column='ParentId', primary_key=True)  # Field name made lowercase.
    parentdesc = models.TextField(db_column='ParentDesc', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblParentMenu'


class Tblplant(models.Model):
    plantid = models.BigIntegerField(db_column='plantId', primary_key=True)  # Field name made lowercase.
    plantname = models.CharField(db_column='plantName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.BigIntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.BigIntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='contactPerson', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    plantcode = models.CharField(db_column='plantCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gstnumber = models.CharField(db_column='gstNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPlant'


class Tblplanthistory(models.Model):
    plantid = models.BigIntegerField(db_column='plantId',primary_key=True)  # Field name made lowercase.
    plantname = models.CharField(db_column='plantName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    addressline1 = models.CharField(db_column='addressLine1', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addressline2 = models.CharField(db_column='addressLine2', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    pincode = models.CharField(max_length=15, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    hamletid = models.BigIntegerField(db_column='hamletId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='villageId', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.BigIntegerField(db_column='subDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.BigIntegerField(db_column='districtId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='stateId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='countryId', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='contactPerson', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    emailaddress = models.CharField(db_column='emailAddress', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    plantcode = models.CharField(db_column='plantCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='otherCode', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gstnumber = models.CharField(db_column='gstNumber', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='HistoryTimeStamp', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='HistoryCreatedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPlantHistory'


class Tblprdabout(models.Model):
    aboutid = models.AutoField(db_column='AboutID', primary_key=True)  # Field name made lowercase.
    aboutapplicationen = models.TextField(db_column='AboutApplicationEn', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    aboutcompanyen = models.TextField(db_column='AboutCompanyEn', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    aboutapplicationhi = models.TextField(db_column='AboutApplicationHi', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    aboutcompanyhi = models.TextField(db_column='AboutCompanyHi', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=200, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    mobile = models.CharField(db_column='Mobile', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdAbout'


class Tblprdadminusers(models.Model):
    adminuserid = models.AutoField(db_column='AdminUserID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    mobile = models.CharField(db_column='Mobile', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdAdminUsers'


class Tblprdfarmersettings(models.Model):
    farmerfirebaseid = models.BigAutoField(db_column='FarmerFirebaseID', primary_key=True)  # Field name made lowercase.
    farmerid = models.BigIntegerField(db_column='FarmerId')  # Field name made lowercase.
    phonenumber = models.CharField(db_column='PhoneNumber', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    deviceid = models.CharField(db_column='DeviceId', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    firebasetoken = models.CharField(db_column='FirebaseToken', max_length=300, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    defaultlanguage = models.IntegerField(db_column='DefaultLanguage')  # Field name made lowercase.
    firstlogindate = models.DateTimeField(db_column='FirstLoginDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdFarmerSettings'


class Tblprdnews(models.Model):
    newsid = models.AutoField(db_column='NewsID', primary_key=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='PlantID')  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='MccID')  # Field name made lowercase.
    mstcentercode = models.BigIntegerField(db_column='MstCenterCode')  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='SocietyCode')  # Field name made lowercase.
    titleen = models.CharField(db_column='TitleEn', max_length=200, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    descriptionen = models.TextField(db_column='DescriptionEn', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    titlehi = models.CharField(db_column='TitleHi', max_length=200, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    descriptionhi = models.TextField(db_column='DescriptionHi', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    url = models.CharField(db_column='Url', max_length=500, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    thumbnail = models.CharField(db_column='Thumbnail', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate')  # Field name made lowercase.
    modifieddate = models.DateTimeField(db_column='ModifiedDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdNews'


class Tblprdnotificationstatus(models.Model):
    statusid = models.AutoField(db_column='StatusID', primary_key=True)  # Field name made lowercase.
    notificationid = models.IntegerField(db_column='NotificationID')  # Field name made lowercase.
    farmerid = models.BigIntegerField(db_column='FarmerId')  # Field name made lowercase.
    sentdatetime = models.DateTimeField(db_column='SentDateTime')  # Field name made lowercase.
    sentstatus = models.CharField(db_column='SentStatus', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    readstatus = models.BooleanField(db_column='ReadStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdNotificationStatus'


class Tblprdnotifications(models.Model):
    notificationid = models.AutoField(db_column='NotificationID', primary_key=True)  # Field name made lowercase.
    notificationto = models.IntegerField(db_column='NotificationTo')  # Field name made lowercase.
    titleen = models.TextField(db_column='TitleEn', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    titlehi = models.TextField(db_column='TitleHi', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    descriptionen = models.TextField(db_column='DescriptionEn', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    descriptionhi = models.TextField(db_column='DescriptionHi', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    thumbnail = models.CharField(db_column='Thumbnail', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate')  # Field name made lowercase.
    modifieddate = models.DateTimeField(db_column='ModifiedDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPrdNotifications'


class Tblpropmst(models.Model):
    propid = models.AutoField(db_column='PropID', primary_key=True)  # Field name made lowercase.
    propname = models.CharField(db_column='PropName', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    proptype = models.CharField(db_column='PropType', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MID', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblPropMst'


class Tblratedetail(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    ratecode = models.BigIntegerField(db_column='RateCode', blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(db_column='Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lr = models.DecimalField(db_column='LR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.
    ratetype = models.IntegerField(db_column='RateType', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    ipaddress = models.CharField(db_column='IpAddress', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateDetail'


class TblratedetailOld(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    ratecode = models.BigIntegerField(db_column='RateCode', blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(db_column='Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.
    ratetype = models.IntegerField(db_column='RateType', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    ipaddress = models.CharField(db_column='IpAddress', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateDetail_OLD'


class Tblrateformula(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    formulaid = models.BigIntegerField(db_column='formulaId')  # Field name made lowercase.
    ratetypeid = models.ForeignKey('Tblratetype', models.DO_NOTHING, db_column='rateTypeId')  # Field name made lowercase.
    ratecode = models.ForeignKey('Tblrateheader', models.DO_NOTHING, db_column='rateCode')  # Field name made lowercase.
    fromfat = models.DecimalField(db_column='fromFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tofat = models.DecimalField(db_column='toFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fromsnf = models.DecimalField(db_column='fromSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tosnf = models.DecimalField(db_column='toSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    type = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    shift = models.CharField(max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    ipaddress = models.CharField(db_column='ipAddress', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDatetime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='isDelete', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloadtimestamp = models.DateTimeField(db_column='downloadTimestamp', blank=True, null=True)  # Field name made lowercase.
    srno = models.IntegerField(db_column='srNo', blank=True, null=True)  # Field name made lowercase.
    pattern = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblRateFormula'


class Tblrateheader(models.Model):
    ratecode = models.BigIntegerField(db_column='RateCode', primary_key=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    effectiveshift = models.CharField(db_column='EffectiveShift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    buffcommission = models.DecimalField(db_column='buffCommission', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cowcommission = models.DecimalField(db_column='cowCommission', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pattern = models.IntegerField(blank=True, null=True)
    iseffectivedatedynamic = models.BooleanField(db_column='isEffectiveDateDynamic', blank=True, null=True)  # Field name made lowercase.
    userlayerid = models.IntegerField(db_column='userLayerId', blank=True, null=True)  # Field name made lowercase.
    userlayerreferenceid = models.BigIntegerField(db_column='userLayerReferenceId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateHeader'


class Tblratemapping(models.Model):
    rowid = models.AutoField(db_column='RowID', primary_key=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    plantid = models.BigIntegerField(db_column='PlantId', blank=True, null=True)  # Field name made lowercase.
    mccid = models.BigIntegerField(db_column='MCCId', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='CenterCode', blank=True, null=True)  # Field name made lowercase.
    routeid = models.BigIntegerField(db_column='RouteId', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate', blank=True, null=True)  # Field name made lowercase.
    effectiveshift = models.CharField(db_column='EffectiveShift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ratetypeid = models.BigIntegerField(db_column='RateTypeId', blank=True, null=True)  # Field name made lowercase.
    ratecode = models.IntegerField(db_column='RateCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='Cid', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloadtimestamp = models.DateTimeField(db_column='downloadTimestamp', blank=True, null=True)  # Field name made lowercase.
    societyothercode = models.CharField(db_column='SocietyOtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='Mid', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    plant_other_code = models.CharField(db_column='Plant_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mcc_other_code = models.CharField(db_column='Mcc_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmc_other_code = models.CharField(db_column='Bmc_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    route_other_code = models.CharField(db_column='Route_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_other_code = models.CharField(db_column='Mpp_Other_Code', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateMapping'


class Tblratestructure(models.Model):
    ratestructureid = models.IntegerField(db_column='RateStructureId', primary_key=True)  # Field name made lowercase.
    ratestructuredesc = models.CharField(db_column='RateStructureDesc', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateStructure'


class Tblratetype(models.Model):
    ratetypeid = models.BigIntegerField(db_column='RateTypeId', primary_key=True)  # Field name made lowercase.
    ratecode = models.BigIntegerField(db_column='RateCode')  # Field name made lowercase.
    issamerateforallmilktype = models.BooleanField(db_column='IsSameRateForAllMilkType')  # Field name made lowercase.
    issamerateforallshift = models.BooleanField(db_column='IsSameRateForAllShift')  # Field name made lowercase.
    description = models.TextField(db_column='Description', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive')  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ismixed = models.BooleanField(db_column='IsMixed', blank=True, null=True)  # Field name made lowercase.
    ratestructure = models.DecimalField(db_column='RateStructure', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRateType'


class Tblroutedetails(models.Model):
    effcode = models.IntegerField(db_column='EffCode',primary_key=True)  # Field name made lowercase.
    rtcode = models.BigIntegerField(db_column='RtCode')  # Field name made lowercase.
    rtname = models.CharField(db_column='RtName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sapcode = models.TextField(db_column='SapCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtccode = models.IntegerField(db_column='RtcCode', blank=True, null=True)  # Field name made lowercase.
    rtschtimem = models.DateTimeField(db_column='RtSchTimeM', blank=True, null=True)  # Field name made lowercase.
    rtschtimee = models.DateTimeField(db_column='RtSchTimeE', blank=True, null=True)  # Field name made lowercase.
    rtkmm = models.DecimalField(db_column='RtKMM', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtkme = models.DecimalField(db_column='RtKME', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtmixmilk = models.BooleanField(db_column='RtMixMilk')  # Field name made lowercase.
    vihicalno = models.IntegerField(db_column='VihicalNo', blank=True, null=True)  # Field name made lowercase.
    fieldofficer = models.IntegerField(db_column='FieldOfficer', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode')  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode')  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(blank=True, null=True)
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRouteDetails'


class Tblroutedetailshistory(models.Model):
    rowid = models.DecimalField(db_column='RowId',primary_key=True, max_digits=20, decimal_places=0)  # Field name made lowercase.
    effcode = models.IntegerField(db_column='EffCode')  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='RtCode')  # Field name made lowercase.
    rtname = models.CharField(db_column='RtName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sapcode = models.TextField(db_column='SapCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtccode = models.IntegerField(db_column='RtcCode', blank=True, null=True)  # Field name made lowercase.
    rtschtimem = models.DateTimeField(db_column='RtSchTimeM', blank=True, null=True)  # Field name made lowercase.
    rtschtimee = models.DateTimeField(db_column='RtSchTimeE', blank=True, null=True)  # Field name made lowercase.
    rtkmm = models.DecimalField(db_column='RtKMM', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtkme = models.DecimalField(db_column='RtKME', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    rtmixmilk = models.BooleanField(db_column='RtMixMilk')  # Field name made lowercase.
    vihicalno = models.IntegerField(db_column='VihicalNo', blank=True, null=True)  # Field name made lowercase.
    fieldofficer = models.IntegerField(db_column='FieldOfficer', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode')  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode')  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRouteDetailsHistory'


class Tblroutetiming(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate', blank=True, null=True)  # Field name made lowercase.
    routecode = models.IntegerField(db_column='RouteCode', blank=True, null=True)  # Field name made lowercase.
    scheduledtimem = models.TimeField(db_column='ScheduledTimeM', blank=True, null=True)  # Field name made lowercase.
    scheduledtimee = models.TimeField(db_column='ScheduledTimeE', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(blank=True, null=True)
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblRouteTiming'


class Tblsmsregister(models.Model):
    registerid = models.BigAutoField(db_column='RegisterId', primary_key=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='SocietyCode', blank=True, null=True)  # Field name made lowercase.
    routecode = models.BigIntegerField(db_column='RouteCode', blank=True, null=True)  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate', blank=True, null=True)  # Field name made lowercase.
    message = models.TextField(db_column='Message', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bweight = models.DecimalField(db_column='BWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bfat = models.DecimalField(db_column='BFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bsnf = models.DecimalField(db_column='BSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cweight = models.DecimalField(db_column='CWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cfat = models.DecimalField(db_column='CFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    csnf = models.DecimalField(db_column='CSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mweight = models.DecimalField(db_column='MWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mfat = models.DecimalField(db_column='MFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    msnf = models.DecimalField(db_column='MSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mobileno = models.TextField(db_column='MobileNo', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    collectioncode = models.BigIntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    deliverydate = models.DateTimeField(db_column='DeliveryDate', blank=True, null=True)  # Field name made lowercase.
    msgid = models.CharField(db_column='MsgId', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    is_delivered = models.BooleanField(db_column='Is_delivered', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    messagestring = models.TextField(db_column='MessageString', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    messageresponse = models.TextField(db_column='MessageResponse', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSMSRegister'


class Tblsmstemplatemapping(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='Companyid', blank=True, null=True)  # Field name made lowercase.
    smscredentialid = models.BigIntegerField(db_column='SmsCredentialid', blank=True, null=True)  # Field name made lowercase.
    smstemplateid = models.BigIntegerField(db_column='SmsTemplateId', blank=True, null=True)  # Field name made lowercase.
    smstype = models.CharField(db_column='SmsType', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSMSTemplateMapping'


class Tblsettings(models.Model):
    totalcenters = models.IntegerField(db_column='TotalCenters',blank=True, null=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    centername = models.CharField(db_column='CenterName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    traysize = models.IntegerField(db_column='TraySize', blank=True, null=True)  # Field name made lowercase.
    backuppath = models.CharField(db_column='BackupPath', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    canwt = models.DecimalField(db_column='CanWt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ismanual = models.BooleanField(db_column='IsManual', blank=True, null=True)  # Field name made lowercase.
    isautomatic = models.BooleanField(db_column='IsAutomatic', blank=True, null=True)  # Field name made lowercase.
    ishangingbowl = models.BooleanField(db_column='IsHangingBowl', blank=True, null=True)  # Field name made lowercase.
    isweightround = models.BooleanField(db_column='IsWeightRound', blank=True, null=True)  # Field name made lowercase.
    weightroundby = models.IntegerField(db_column='WeightRoundBy', blank=True, null=True)  # Field name made lowercase.
    canaverageweight = models.DecimalField(db_column='CanAverageWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cancapacity = models.DecimalField(db_column='CanCapacity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    daysavg = models.IntegerField(db_column='DaysAvg', blank=True, null=True)  # Field name made lowercase.
    updateagain = models.BooleanField(db_column='UpdateAgain', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.BooleanField(db_column='SadaCan', blank=True, null=True)  # Field name made lowercase.
    labavgdays = models.IntegerField(db_column='LabAvgDays', blank=True, null=True)  # Field name made lowercase.
    snf_formula = models.IntegerField(db_column='SNF_Formula', blank=True, null=True)  # Field name made lowercase.
    snfconst = models.FloatField(db_column='SnfConst', blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='MaxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='MaxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='MaxCowSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffat = models.DecimalField(db_column='MaxBufFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufclr = models.DecimalField(db_column='MaxBufClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufsnf = models.DecimalField(db_column='MaxBufSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='MaxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='MaxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='MaxMixSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffat = models.DecimalField(db_column='MinBufFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='MinCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='MinMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iscountfatindockdataupdate = models.BooleanField(db_column='IsCountFatInDockDataUpdate', blank=True, null=True)  # Field name made lowercase.
    issnfround = models.BooleanField(db_column='IsSNFRound', blank=True, null=True)  # Field name made lowercase.
    snfformula = models.IntegerField(db_column='SNFFormula', blank=True, null=True)  # Field name made lowercase.
    roundingbychar = models.IntegerField(db_column='RoundingByChar', blank=True, null=True)  # Field name made lowercase.
    snfrounding = models.IntegerField(db_column='SNFRounding', blank=True, null=True)  # Field name made lowercase.
    isdisplay = models.BooleanField(db_column='IsDisplay', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    issoccodemanual = models.BooleanField(db_column='IsSocCodeManual', blank=True, null=True)  # Field name made lowercase.
    companycode = models.ForeignKey(Tblmstcompany, models.DO_NOTHING, db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    bcconverter = models.BooleanField(db_column='BcConverter', blank=True, null=True)  # Field name made lowercase.
    bcconverterfat = models.DecimalField(db_column='BcConverterFat', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    isdockmanual = models.BooleanField(db_column='IsDockManual', blank=True, null=True)  # Field name made lowercase.
    islabmanual = models.BooleanField(db_column='IsLabManual', blank=True, null=True)  # Field name made lowercase.
    fatdefaultsour = models.DecimalField(db_column='FatDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultsour = models.DecimalField(db_column='SnfDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fatdefaultcurd = models.DecimalField(db_column='FatDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultcurd = models.DecimalField(db_column='SnfDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockafterdecimal = models.SmallIntegerField(db_column='DockAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    analyser = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='Analyser', blank=True, null=True)  # Field name made lowercase.
    analyserbaudrate = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='AnalyserBaudRate', related_name='tblsettings_analyserbaudrate_set', blank=True, null=True)  # Field name made lowercase.
    analyserport = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='AnalyserPort', related_name='tblsettings_analyserport_set', blank=True, null=True)  # Field name made lowercase.
    weighingscale = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='WeighingScale', related_name='tblsettings_weighingscale_set', blank=True, null=True)  # Field name made lowercase.
    weighingbaudrate = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='WeighingBaudRate', related_name='tblsettings_weighingbaudrate_set', blank=True, null=True)  # Field name made lowercase.
    weighingport = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='WeighingPort', related_name='tblsettings_weighingport_set', blank=True, null=True)  # Field name made lowercase.
    display = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='Display', related_name='tblsettings_display_set', blank=True, null=True)  # Field name made lowercase.
    displaybaudrate = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='DisplayBaudRate', related_name='tblsettings_displaybaudrate_set', blank=True, null=True)  # Field name made lowercase.
    displayport = models.ForeignKey(Tblpropmst, models.DO_NOTHING, db_column='DisplayPort', related_name='tblsettings_displayport_set', blank=True, null=True)  # Field name made lowercase.
    fatafterdecimal = models.IntegerField(db_column='FatAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    snfafterdecimal = models.IntegerField(db_column='SnfAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    isfatround = models.BooleanField(db_column='IsFatRound', blank=True, null=True)  # Field name made lowercase.
    time = models.BooleanField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    date = models.BooleanField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    sampleno = models.BooleanField(db_column='SampleNo', blank=True, null=True)  # Field name made lowercase.
    fat = models.BooleanField(db_column='Fat', blank=True, null=True)  # Field name made lowercase.
    snf = models.BooleanField(db_column='Snf', blank=True, null=True)  # Field name made lowercase.
    lactose = models.BooleanField(db_column='Lactose', blank=True, null=True)  # Field name made lowercase.
    protein = models.BooleanField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    water = models.BooleanField(db_column='Water', blank=True, null=True)  # Field name made lowercase.
    density = models.BooleanField(db_column='Density', blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.BooleanField(db_column='FreezingPoint', blank=True, null=True)  # Field name made lowercase.
    urea = models.BooleanField(db_column='Urea', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.BooleanField(db_column='Maltodex', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.BooleanField(db_column='Ammsulp', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.BooleanField(db_column='Sucrose', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.BooleanField(db_column='Abnormal', blank=True, null=True)  # Field name made lowercase.
    errorname = models.BooleanField(db_column='ErrorName', blank=True, null=True)  # Field name made lowercase.
    badsample = models.BooleanField(db_column='BadSample', blank=True, null=True)  # Field name made lowercase.
    isallcenterforroute = models.BooleanField(db_column='IsAllCenterForRoute', blank=True, null=True)  # Field name made lowercase.
    labafterdecimal = models.IntegerField(db_column='LabAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    labrounding = models.BooleanField(db_column='LabRounding', blank=True, null=True)  # Field name made lowercase.
    ismixmilkonly = models.BooleanField(db_column='IsMixMilkOnly', blank=True, null=True)  # Field name made lowercase.
    isfarmercollectionduplicate = models.BooleanField(db_column='IsFarmerCollectionDuplicate', blank=True, null=True)  # Field name made lowercase.
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    lrrounding = models.BooleanField(db_column='LRRounding', blank=True, null=True)  # Field name made lowercase.
    allowpaymentcyclelock = models.BooleanField(db_column='AllowPaymentCycleLock', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    milkmode = models.CharField(db_column='MilkMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    minbuffsnf = models.DecimalField(db_column='MinBuffSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfsnf = models.DecimalField(db_column='MinCowfSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfsnf = models.DecimalField(db_column='MinMixfSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSettings'


class Tblsettingshistory(models.Model):
    totalcenters = models.IntegerField(db_column='TotalCenters', blank=True, null=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=70, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    centername = models.CharField(db_column='CenterName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    traysize = models.IntegerField(db_column='TraySize', blank=True, null=True)  # Field name made lowercase.
    backuppath = models.CharField(db_column='BackupPath', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    canwt = models.DecimalField(db_column='CanWt', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ismanual = models.BooleanField(db_column='IsManual', blank=True, null=True)  # Field name made lowercase.
    isautomatic = models.BooleanField(db_column='IsAutomatic', blank=True, null=True)  # Field name made lowercase.
    ishangingbowl = models.BooleanField(db_column='IsHangingBowl', blank=True, null=True)  # Field name made lowercase.
    isweightround = models.BooleanField(db_column='IsWeightRound', blank=True, null=True)  # Field name made lowercase.
    weightroundby = models.IntegerField(db_column='WeightRoundBy', blank=True, null=True)  # Field name made lowercase.
    canaverageweight = models.DecimalField(db_column='CanAverageWeight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cancapacity = models.DecimalField(db_column='CanCapacity', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    daysavg = models.IntegerField(db_column='DaysAvg', blank=True, null=True)  # Field name made lowercase.
    updateagain = models.BooleanField(db_column='UpdateAgain', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.BooleanField(db_column='SadaCan', blank=True, null=True)  # Field name made lowercase.
    labavgdays = models.IntegerField(db_column='LabAvgDays', blank=True, null=True)  # Field name made lowercase.
    snf_formula = models.IntegerField(db_column='SNF_Formula', blank=True, null=True)  # Field name made lowercase.
    snfconst = models.FloatField(db_column='SnfConst', blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='MaxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='MaxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='MaxCowSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffat = models.DecimalField(db_column='MaxBufFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufclr = models.DecimalField(db_column='MaxBufClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufsnf = models.DecimalField(db_column='MaxBufSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='MaxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='MaxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='MaxMixSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffat = models.DecimalField(db_column='MinBufFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='MinCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='MinMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    iscountfatindockdataupdate = models.BooleanField(db_column='IsCountFatInDockDataUpdate', blank=True, null=True)  # Field name made lowercase.
    issnfround = models.BooleanField(db_column='IsSNFRound', blank=True, null=True)  # Field name made lowercase.
    snfformula = models.IntegerField(db_column='SNFFormula', blank=True, null=True)  # Field name made lowercase.
    roundingbychar = models.IntegerField(db_column='RoundingByChar', blank=True, null=True)  # Field name made lowercase.
    snfrounding = models.IntegerField(db_column='SNFRounding', blank=True, null=True)  # Field name made lowercase.
    isdisplay = models.BooleanField(db_column='IsDisplay', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    issoccodemanual = models.BooleanField(db_column='IsSocCodeManual', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    bcconverter = models.BooleanField(db_column='BcConverter', blank=True, null=True)  # Field name made lowercase.
    bcconverterfat = models.DecimalField(db_column='BcConverterFat', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    isdockmanual = models.BooleanField(db_column='IsDockManual', blank=True, null=True)  # Field name made lowercase.
    islabmanual = models.BooleanField(db_column='IsLabManual', blank=True, null=True)  # Field name made lowercase.
    fatdefaultsour = models.DecimalField(db_column='FatDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultsour = models.DecimalField(db_column='SnfDefaultSour', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fatdefaultcurd = models.DecimalField(db_column='FatDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snfdefaultcurd = models.DecimalField(db_column='SnfDefaultCurd', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockafterdecimal = models.SmallIntegerField(db_column='DockAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    analyser = models.IntegerField(db_column='Analyser', blank=True, null=True)  # Field name made lowercase.
    analyserbaudrate = models.IntegerField(db_column='AnalyserBaudRate', blank=True, null=True)  # Field name made lowercase.
    analyserport = models.IntegerField(db_column='AnalyserPort', blank=True, null=True)  # Field name made lowercase.
    weighingscale = models.IntegerField(db_column='WeighingScale', blank=True, null=True)  # Field name made lowercase.
    weighingbaudrate = models.IntegerField(db_column='WeighingBaudRate', blank=True, null=True)  # Field name made lowercase.
    weighingport = models.IntegerField(db_column='WeighingPort', blank=True, null=True)  # Field name made lowercase.
    display = models.IntegerField(db_column='Display', blank=True, null=True)  # Field name made lowercase.
    displaybaudrate = models.IntegerField(db_column='DisplayBaudRate', blank=True, null=True)  # Field name made lowercase.
    displayport = models.IntegerField(db_column='DisplayPort', blank=True, null=True)  # Field name made lowercase.
    fatafterdecimal = models.IntegerField(db_column='FatAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    snfafterdecimal = models.IntegerField(db_column='SnfAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    isfatround = models.BooleanField(db_column='IsFatRound', blank=True, null=True)  # Field name made lowercase.
    time = models.BooleanField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    date = models.BooleanField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    sampleno = models.BooleanField(db_column='SampleNo', blank=True, null=True)  # Field name made lowercase.
    fat = models.BooleanField(db_column='Fat', blank=True, null=True)  # Field name made lowercase.
    snf = models.BooleanField(db_column='Snf', blank=True, null=True)  # Field name made lowercase.
    lactose = models.BooleanField(db_column='Lactose', blank=True, null=True)  # Field name made lowercase.
    protein = models.BooleanField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    water = models.BooleanField(db_column='Water', blank=True, null=True)  # Field name made lowercase.
    density = models.BooleanField(db_column='Density', blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.BooleanField(db_column='FreezingPoint', blank=True, null=True)  # Field name made lowercase.
    urea = models.BooleanField(db_column='Urea', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.BooleanField(db_column='Maltodex', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.BooleanField(db_column='Ammsulp', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.BooleanField(db_column='Sucrose', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.BooleanField(db_column='Abnormal', blank=True, null=True)  # Field name made lowercase.
    errorname = models.BooleanField(db_column='ErrorName', blank=True, null=True)  # Field name made lowercase.
    badsample = models.BooleanField(db_column='BadSample', blank=True, null=True)  # Field name made lowercase.
    isallcenterforroute = models.BooleanField(db_column='IsAllCenterForRoute', blank=True, null=True)  # Field name made lowercase.
    labafterdecimal = models.IntegerField(db_column='LabAfterDecimal', blank=True, null=True)  # Field name made lowercase.
    labrounding = models.BooleanField(db_column='LabRounding', blank=True, null=True)  # Field name made lowercase.
    ismixmilkonly = models.BooleanField(db_column='IsMixMilkOnly', blank=True, null=True)  # Field name made lowercase.
    isfarmercollectionduplicate = models.BooleanField(db_column='IsFarmerCollectionDuplicate', blank=True, null=True)  # Field name made lowercase.
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    logcreatedby = models.BigIntegerField(db_column='logCreatedBy', blank=True, null=True)  # Field name made lowercase.
    logcreateddatetime = models.DateTimeField(db_column='logCreatedDatetime', blank=True, null=True)  # Field name made lowercase.
    lrrounding = models.BooleanField(db_column='LRRounding', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSettingsHistory'


class Tblsmpsregister(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    collectionpointcode = models.BigIntegerField(db_column='collectionPointCode')  # Field name made lowercase.
    smpsid = models.CharField(db_column='smpsId', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    companycode = models.IntegerField(db_column='companyCode')  # Field name made lowercase.
    smpstype = models.CharField(db_column='smpsType', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId')  # Field name made lowercase.
    cuserdatetime = models.DateTimeField(db_column='cUserDatetime')  # Field name made lowercase.
    collectionpointtype = models.IntegerField(db_column='collectionPointType', blank=True, null=True)  # Field name made lowercase.
    isregistered = models.BooleanField(db_column='isRegistered', blank=True, null=True)  # Field name made lowercase.
    registrationdatetime = models.DateTimeField(db_column='registrationDatetime', blank=True, null=True)  # Field name made lowercase.
    registeredby = models.CharField(db_column='registeredBy', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    iscollectionpointonline = models.BooleanField(db_column='isCollectionPointOnline', blank=True, null=True)  # Field name made lowercase.
    expirationdatetime = models.DateTimeField(db_column='expirationDatetime', blank=True, null=True)  # Field name made lowercase.
    withdrawaldatetime = models.DateTimeField(db_column='withdrawalDatetime', blank=True, null=True)  # Field name made lowercase.
    withdrawnby = models.CharField(db_column='withdrawnBy', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    installationmachinename = models.CharField(db_column='installationMachineName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    installationmachinemac = models.CharField(db_column='installationMachineMAC', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otp = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    isotpexpired = models.BooleanField(db_column='isOtpExpired', blank=True, null=True)  # Field name made lowercase.
    otpdatetime = models.DateTimeField(db_column='otpDatetime', blank=True, null=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    subscriptionenddate = models.DateTimeField(db_column='subscriptionEndDate', blank=True, null=True)  # Field name made lowercase.
    apppassword = models.CharField(db_column='appPassword', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastonlinedatetime = models.DateTimeField(db_column='lastOnlineDatetime', blank=True, null=True)  # Field name made lowercase.
    noofbackdays = models.IntegerField(db_column='noOfBackDays', blank=True, null=True)  # Field name made lowercase.
    smpsidtimezone = models.CharField(db_column='smpsIdTimezone', max_length=60, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    paymentcredid = models.BigIntegerField(db_column='paymentCredId', blank=True, null=True)  # Field name made lowercase.
    isautopaymentenabled = models.BooleanField(db_column='isAutoPaymentEnabled', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    installationdatetime = models.DateTimeField(db_column='installationDatetime', blank=True, null=True)  # Field name made lowercase.
    secretkey = models.CharField(db_column='secretKey', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdemo = models.BooleanField(db_column='isDemo', blank=True, null=True)  # Field name made lowercase.
    islive = models.BooleanField(db_column='isLive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSmpsRegister'


class Tblsmscredential(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    smscredentialid = models.BigIntegerField(db_column='SmsCredentialId')  # Field name made lowercase.
    userid = models.CharField(db_column='UserId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    senderid = models.CharField(db_column='SenderId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='CompanyId', blank=True, null=True)  # Field name made lowercase.
    baseurl = models.CharField(db_column='BaseUrl', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sampleurl = models.CharField(db_column='SampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSmsCredential'


class Tblsmssetting(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='companyCode')  # Field name made lowercase.
    bmcsmsstring = models.CharField(db_column='bmcSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcpeid = models.CharField(db_column='bmcPeId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmctemplateid = models.CharField(db_column='bmcTemplateId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcsamplesmsstring = models.CharField(db_column='bmcSampleSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcuserid = models.CharField(db_column='bmcUserId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcpassword = models.CharField(db_column='bmcPassword', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcsenderid = models.CharField(db_column='bmcSenderId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcbaseurl = models.CharField(db_column='bmcBaseUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcsampleurl = models.CharField(db_column='bmcSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcbalanceurl = models.CharField(db_column='bmcBalanceUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcbalancesampleurl = models.CharField(db_column='bmcBalanceSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcresponseurl = models.CharField(db_column='bmcResponseUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    bmcresponsesampleurl = models.CharField(db_column='bmcResponseSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmersmsstring = models.CharField(db_column='farmerSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerpeid = models.CharField(db_column='farmerPeId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmertemplateid = models.CharField(db_column='farmerTemplateId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmersamplesmsstring = models.CharField(db_column='farmerSampleSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmeruserid = models.CharField(db_column='farmerUserId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerpassword = models.CharField(db_column='farmerPassword', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmersenderid = models.CharField(db_column='farmerSenderId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerbaseurl = models.CharField(db_column='farmerBaseUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmersampleurl = models.CharField(db_column='farmerSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerbalanceurl = models.CharField(db_column='farmerBalanceUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerbalancesampleurl = models.CharField(db_column='farmerBalanceSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpsmsstring = models.CharField(db_column='otpSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otppeid = models.CharField(db_column='otpPeId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otptemplateid = models.CharField(db_column='otpTemplateId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpsamplesmsstring = models.CharField(db_column='otpSampleSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpuserid = models.CharField(db_column='otpUserId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otppassword = models.CharField(db_column='otpPassword', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpsenderid = models.CharField(db_column='otpSenderId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpbaseurl = models.CharField(db_column='otpBaseUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpsampleurl = models.CharField(db_column='otpSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpbalanceurl = models.CharField(db_column='otpBalanceUrl', max_length=500, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otpbalancesampleurl = models.CharField(db_column='otpBalanceSampleUrl', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    musercode = models.BigIntegerField(db_column='mUserCode', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSmsSetting'


class Tblsmstemplate(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    smstemplateid = models.BigIntegerField(db_column='SmsTemplateId')  # Field name made lowercase.
    smsstring = models.CharField(db_column='SmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    peid = models.CharField(db_column='PeId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    templateid = models.CharField(db_column='TemplateId', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='CompanyId', blank=True, null=True)  # Field name made lowercase.
    samplesmsstring = models.CharField(db_column='SampleSmsString', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSmsTemplate'


class Tblsociety(models.Model):
    soccode = models.BigIntegerField(db_column='SocCode',primary_key=True)  # Field name made lowercase.
    socname = models.CharField(db_column='socName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    socname2 = models.CharField(db_column='socName2', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    soccodetxt = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    companycode = models.IntegerField(db_column='CompanyCode')  # Field name made lowercase.
    rtcode = models.BigIntegerField(db_column='rtCode', blank=True, null=True)  # Field name made lowercase.
    saprtcode = models.TextField(db_column='SapRtCode', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fscode = models.IntegerField(db_column='fsCode', blank=True, null=True)  # Field name made lowercase.
    tlkcode = models.IntegerField(db_column='tlkCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode')  # Field name made lowercase.
    mobileno = models.CharField(max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    isdemo = models.BooleanField(db_column='IsDemo', blank=True, null=True)  # Field name made lowercase.
    islive = models.BooleanField(db_column='IsLive', blank=True, null=True)  # Field name made lowercase.
    installtiondate = models.DateTimeField(db_column='InstalltionDate', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.BigIntegerField(db_column='BankCode', blank=True, null=True)  # Field name made lowercase.
    accountno = models.CharField(db_column='AccountNo', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    adharno = models.CharField(db_column='AdharNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    agentname = models.CharField(db_column='AgentName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sapplantcode = models.IntegerField(db_column='SapPlantCode', blank=True, null=True)  # Field name made lowercase.
    dstcode = models.BigIntegerField(db_column='dstCode', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.BigIntegerField(db_column='SubDistrictId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.BigIntegerField(db_column='VillageId', blank=True, null=True)  # Field name made lowercase.
    hamletid = models.BigIntegerField(db_column='HamletId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.BigIntegerField(db_column='CountryId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.BigIntegerField(db_column='StateId', blank=True, null=True)  # Field name made lowercase.
    bankbranchname = models.CharField(db_column='BankBranchName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsc = models.CharField(db_column='IFSC', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountname = models.CharField(db_column='AccountName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    excodeoftahsilcode = models.CharField(db_column='ExCodeofTahsilCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='ContactPerson', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    panno = models.CharField(db_column='PanNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    securityamount = models.DecimalField(db_column='SecurityAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    referenceno = models.CharField(db_column='ReferenceNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    aggrementno = models.CharField(db_column='AggrementNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    aggerementexpirydate = models.DateField(db_column='AggerementExpiryDate', blank=True, null=True)  # Field name made lowercase.
    securitychequeno_1lakhrs = models.CharField(db_column='SecurityChequeNo_1LakhRs', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    securitychequeno_100rs = models.CharField(db_column='SecurityChequeNo_100Rs', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(blank=True, null=True)
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    effectivedate = models.DateField(db_column='EffectiveDate', blank=True, null=True)  # Field name made lowercase.
    effectiveshift = models.CharField(db_column='EffectiveShift', max_length=10, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSociety'


class Tblsocietyhistory(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode')  # Field name made lowercase.
    socname = models.CharField(db_column='socName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    socname2 = models.CharField(db_column='socName2', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    soccodetxt = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    companycode = models.BigIntegerField(db_column='CompanyCode')  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='rtCode', blank=True, null=True)  # Field name made lowercase.
    saprtcode = models.CharField(db_column='SapRtCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fscode = models.IntegerField(db_column='fsCode', blank=True, null=True)  # Field name made lowercase.
    tlkcode = models.IntegerField(db_column='tlkCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    mobileno = models.CharField(max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    isdemo = models.BooleanField(db_column='IsDemo', blank=True, null=True)  # Field name made lowercase.
    islive = models.BooleanField(db_column='IsLive', blank=True, null=True)  # Field name made lowercase.
    installtiondate = models.DateTimeField(db_column='InstalltionDate', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    bankcode = models.IntegerField(db_column='BankCode', blank=True, null=True)  # Field name made lowercase.
    accountno = models.CharField(db_column='AccountNo', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    adharno = models.CharField(db_column='AdharNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    agentname = models.CharField(db_column='AgentName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sapplantcode = models.IntegerField(db_column='SapPlantCode', blank=True, null=True)  # Field name made lowercase.
    dstcode = models.IntegerField(db_column='dstCode', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='SubDistrictId', blank=True, null=True)  # Field name made lowercase.
    villageid = models.IntegerField(db_column='VillageId', blank=True, null=True)  # Field name made lowercase.
    hamletid = models.IntegerField(db_column='HamletId', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='CountryId', blank=True, null=True)  # Field name made lowercase.
    stateid = models.IntegerField(db_column='StateId', blank=True, null=True)  # Field name made lowercase.
    bankbranchname = models.CharField(db_column='BankBranchName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ifsc = models.CharField(db_column='IFSC', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    accountname = models.CharField(db_column='AccountName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    excodeoftahsilcode = models.CharField(db_column='ExCodeofTahsilCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contactperson = models.CharField(db_column='ContactPerson', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contactno = models.CharField(db_column='ContactNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    panno = models.CharField(db_column='PanNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    securityamount = models.DecimalField(db_column='SecurityAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    paymentmode = models.CharField(db_column='PaymentMode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    referenceno = models.CharField(db_column='ReferenceNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    aggrementno = models.CharField(db_column='AggrementNo', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    aggerementexpirydate = models.CharField(db_column='AggerementExpiryDate', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    securitychequeno_1lakhrs = models.CharField(db_column='SecurityChequeNo_1LakhRs', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    securitychequeno_100rs = models.CharField(db_column='SecurityChequeNo_100Rs', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    historytimestamp = models.DateTimeField(db_column='HistoryTimeStamp', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='HistoryCreatedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSocietyHistory'


class Tblsocietysetting(models.Model):
    rowid = models.AutoField(db_column='RowID', primary_key=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='SocietyCode', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='CenterCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    milkmode = models.CharField(db_column='MilkMode', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='MaxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='MaxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='MaxCowSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffalofat = models.DecimalField(db_column='MaxBuffaloFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffaloclr = models.DecimalField(db_column='MaxBuffaloClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffalosnf = models.DecimalField(db_column='MaxBuffaloSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='MaxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='MaxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='MaxMixSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffalofat = models.DecimalField(db_column='MinBuffaloFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='MinCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='MinMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    mincowsnf = models.DecimalField(db_column='MinCowSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffsnf = models.DecimalField(db_column='MinBuffSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixsnf = models.DecimalField(db_column='MinMixSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    analyzercode = models.BigIntegerField(db_column='analyzerCode', blank=True, null=True)  # Field name made lowercase.
    weightmachinecode = models.BigIntegerField(db_column='weightMachineCode', blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.BooleanField(db_column='isQtyAuto', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.BooleanField(db_column='isQltyAuto', blank=True, null=True)  # Field name made lowercase.
    allowratezero = models.BooleanField(db_column='allowRateZero', blank=True, null=True)  # Field name made lowercase.
    printercode = models.BigIntegerField(db_column='printerCode', blank=True, null=True)  # Field name made lowercase.
    analyzerinterfacetype = models.CharField(db_column='analyzerInterfaceType', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    weightmachineinterfacetype = models.CharField(db_column='weightMachineInterfaceType', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    printerinterfacetype = models.CharField(db_column='printerInterfaceType', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autotare = models.BooleanField(db_column='autoTare', blank=True, null=True)  # Field name made lowercase.
    enableprintslip = models.BooleanField(db_column='enablePrintSlip', blank=True, null=True)  # Field name made lowercase.
    enableshiftrange = models.BooleanField(db_column='enableShiftRange', blank=True, null=True)  # Field name made lowercase.
    morningstarttime = models.TimeField(db_column='morningStartTime', blank=True, null=True)  # Field name made lowercase.
    morningendtime = models.TimeField(db_column='morningEndTime', blank=True, null=True)  # Field name made lowercase.
    eveningstarttime = models.TimeField(db_column='eveningStartTime', blank=True, null=True)  # Field name made lowercase.
    eveningendtime = models.TimeField(db_column='eveningEndTime', blank=True, null=True)  # Field name made lowercase.
    displaycode = models.BigIntegerField(db_column='displayCode', blank=True, null=True)  # Field name made lowercase.
    displayinterfacetype = models.CharField(db_column='displayInterfaceType', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    enabledisplay = models.BooleanField(db_column='enableDisplay', blank=True, null=True)  # Field name made lowercase.
    enablemachinecommand = models.BooleanField(db_column='enableMachineCommand', blank=True, null=True)  # Field name made lowercase.
    allowcreatemember = models.BooleanField(db_column='allowCreateMember', blank=True, null=True)  # Field name made lowercase.
    allowcollectionmodification = models.BooleanField(db_column='allowCollectionModification', blank=True, null=True)  # Field name made lowercase.
    allowcollectiondelete = models.BooleanField(db_column='allowCollectionDelete', blank=True, null=True)  # Field name made lowercase.
    allowcollectionreprint = models.BooleanField(db_column='allowCollectionReprint', blank=True, null=True)  # Field name made lowercase.
    enablecollectionsetting = models.BooleanField(db_column='enableCollectionSetting', blank=True, null=True)  # Field name made lowercase.
    enabledevicesetting = models.BooleanField(db_column='enableDeviceSetting', blank=True, null=True)  # Field name made lowercase.
    enablelocalsale = models.BooleanField(db_column='enableLocalSale', blank=True, null=True)  # Field name made lowercase.
    localsalerateperltr = models.DecimalField(db_column='localSaleRatePerLtr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dispatchqtyauto = models.BooleanField(db_column='dispatchQtyAuto', blank=True, null=True)  # Field name made lowercase.
    dispatchqltyauto = models.BooleanField(db_column='dispatchQltyAuto', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSocietySetting'


class Tblsocietysettings(models.Model):
    rowid = models.AutoField(db_column='RowID',primary_key=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(db_column='SocCode')  # Field name made lowercase.
    ratetype = models.IntegerField(db_column='RateType', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSocietySettings'


class Tblsoftwareconfig(models.Model):
    isoffline = models.BooleanField(db_column='isOffline', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSoftwareConfig'


class Tblstaging(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateField(db_column='DumpDate', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.CharField(db_column='DumpTime', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    farmerid = models.BigIntegerField(db_column='FarmerId', blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    insertmode = models.CharField(db_column='InsertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isqltyauto = models.CharField(db_column='IsQltyAuto', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isqtyauto = models.CharField(db_column='IsQtyAuto', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rtpl = models.DecimalField(db_column='Rtpl', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId', blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='Snf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lr = models.DecimalField(db_column='LR', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    totalamount = models.DecimalField(db_column='TotalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=5, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    weightliter = models.DecimalField(db_column='WeightLiter', max_digits=18, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    can = models.IntegerField(db_column='Can', blank=True, null=True)  # Field name made lowercase.
    mppcode = models.BigIntegerField(db_column='Mppcode', blank=True, null=True)  # Field name made lowercase.
    batchno = models.CharField(db_column='BatchNo', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    refranceid = models.BigIntegerField(db_column='RefranceId', blank=True, null=True)  # Field name made lowercase.
    isvalidated = models.BooleanField(db_column='IsValidated', blank=True, null=True)  # Field name made lowercase.
    isprocess = models.BooleanField(db_column='IsProcess', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    processdate = models.DateTimeField(db_column='ProcessDate', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    imei_no = models.CharField(db_column='IMEI_No', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblStaging'


class Tblstate(models.Model):
    stateid = models.IntegerField(db_column='StateId', primary_key=True)  # Field name made lowercase.
    statename = models.CharField(db_column='StateName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    statecapital = models.CharField(db_column='StateCapital', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='CountryId', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    designation = models.CharField(db_column='Designation', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    gstcode = models.CharField(db_column='GstCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblState'


class Tblsubdistrict(models.Model):
    subdistrictid = models.IntegerField(db_column='SubDistrictId', primary_key=True)  # Field name made lowercase.
    subdistrictname = models.CharField(db_column='SubDistrictName', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='DistrictId', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblSubDistrict'


class Tbltaluka(models.Model):
    tlkcode = models.IntegerField(db_column='tlkCode', primary_key=True)  # Field name made lowercase.
    tlkname = models.CharField(db_column='tlkName', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    dstcode = models.IntegerField(db_column='dstCode')  # Field name made lowercase.
    companycode = models.ForeignKey(Tblmstcompany, models.DO_NOTHING, db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.ForeignKey('Tbluser', models.DO_NOTHING, db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.ForeignKey('Tbluser', models.DO_NOTHING, db_column='MId', related_name='tbltaluka_mid_set', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTaluka'


class Tbltruckarrival(models.Model):
    rtcode = models.IntegerField(db_column='rtCode', primary_key=True)  # Field name made lowercase. The composite primary key (rtCode, DumpDate, Shift, CntCode, CollectionCode) found, that is not supported. The first column is selected.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    arrivaltime = models.DateTimeField(db_column='ArrivalTime', blank=True, null=True)  # Field name made lowercase.
    truckno = models.CharField(db_column='TruckNo', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    schtime = models.DateTimeField(db_column='SchTime', blank=True, null=True)  # Field name made lowercase.
    arrivaldelay = models.IntegerField(db_column='ArrivalDelay', blank=True, null=True)  # Field name made lowercase.
    arrivaldelaytxt = models.CharField(db_column='ArrivalDelayTxt', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    arrivaltimetxt = models.CharField(db_column='ArrivalTimeTxt', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    schtimetxt = models.CharField(db_column='SchTimeTxt', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companycode = models.CharField(db_column='CompanyCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.BigIntegerField(db_column='CntCode')  # Field name made lowercase.
    collectioncode = models.BigIntegerField(db_column='CollectionCode')  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='AutoID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTruckArrival'
        unique_together = (('rtcode', 'dumpdate', 'shift', 'cntcode', 'collectioncode'),)


class Tbltruckarrivalhistory(models.Model):
    rowid = models.BigAutoField(db_column='rowId', primary_key=True)  # Field name made lowercase.
    routeid = models.IntegerField(db_column='routeId')  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='dumpDate')  # Field name made lowercase.
    shift = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI')
    arrivaltime = models.DateTimeField(db_column='arrivalTime', blank=True, null=True)  # Field name made lowercase.
    vehicledescription = models.CharField(db_column='vehicleDescription', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    scheduletime = models.DateTimeField(db_column='scheduleTime', blank=True, null=True)  # Field name made lowercase.
    arrivaldelay = models.IntegerField(db_column='arrivalDelay', blank=True, null=True)  # Field name made lowercase.
    arrivaldelaytxt = models.CharField(db_column='arrivalDelayTxt', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    arrivaltimetxt = models.CharField(db_column='arrivalTimeTxt', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    schedulemenutimetxt = models.CharField(db_column='scheduleMenuTimeTxt', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companyid = models.BigIntegerField(db_column='companyId', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDatetime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDatetime', blank=True, null=True)  # Field name made lowercase.
    isuploaded = models.BooleanField(db_column='isUploaded', blank=True, null=True)  # Field name made lowercase.
    centerid = models.IntegerField(db_column='centerId', blank=True, null=True)  # Field name made lowercase.
    collectioncenterid = models.BigIntegerField(db_column='collectionCenterId', blank=True, null=True)  # Field name made lowercase.
    insertmode = models.CharField(db_column='insertMode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    autoid = models.BigIntegerField(db_column='autoId', blank=True, null=True)  # Field name made lowercase.
    historycreatedby = models.BigIntegerField(db_column='historyCreatedBy', blank=True, null=True)  # Field name made lowercase.
    historydatetime = models.DateTimeField(db_column='historyDatetime', blank=True, null=True)  # Field name made lowercase.
    uploaddatetime = models.DateTimeField(db_column='uploadDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblTruckArrivalHistory'


class Tblunit(models.Model):
    rowid = models.AutoField(db_column='RowID',primary_key=True)  # Field name made lowercase.
    unitcode = models.IntegerField(db_column='UnitCode')  # Field name made lowercase.
    unitname = models.TextField(db_column='UnitName', db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    shortdescription = models.TextField(db_column='ShortDescription', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    fulldescription = models.TextField(db_column='FullDescription', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    subunitname = models.TextField(db_column='SubUnitName', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    subshortdescription = models.TextField(db_column='SubShortDescription', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    subfulldescription = models.TextField(db_column='SubFullDescription', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    qtyperunit = models.IntegerField(db_column='QTYPerUnit', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    iscompound = models.BooleanField(db_column='IsCompound', blank=True, null=True)  # Field name made lowercase.
    firstunit = models.IntegerField(db_column='FirstUnit', blank=True, null=True)  # Field name made lowercase.
    secondunit = models.IntegerField(db_column='SecondUnit', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUnit'


class Tbluser(models.Model):
    usrcode = models.IntegerField(db_column='UsrCode', primary_key=True)  # Field name made lowercase.
    usrlevel = models.TextField(db_column='UsrLevel', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    middlename = models.CharField(db_column='MiddleName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    usrname = models.CharField(db_column='UsrName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    usrpassword = models.TextField(db_column='UsrPassword', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otp = models.CharField(db_column='OTP', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isotpexpired = models.BooleanField(db_column='isOTPExpired')  # Field name made lowercase.
    otpdatetimeist = models.DateTimeField(db_column='OTPDateTimeIST', blank=True, null=True)  # Field name made lowercase.
    birthdate = models.DateTimeField(db_column='BirthDate', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    add1 = models.CharField(db_column='Add1', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='PinCode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    country = models.TextField(db_column='Country', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phoneno = models.CharField(db_column='PhoneNo', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contractorname = models.CharField(db_column='ContractorName', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.CharField(db_column='CompanyCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    iscollection = models.BooleanField(db_column='IsCollection', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.IntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    isfieldofficer = models.BooleanField(db_column='IsFieldOfficer', blank=True, null=True)  # Field name made lowercase.
    allowchangepassword = models.BooleanField(db_column='AllowChangePassword', blank=True, null=True)  # Field name made lowercase.
    allowreupdatedockdata = models.BooleanField(db_column='AllowReUpdateDockData', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    img = models.TextField(db_column='Img', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    allowmemberexportonly = models.BooleanField(db_column='AllowMemberExportOnly', blank=True, null=True)  # Field name made lowercase.
    allowrateexportonly = models.BooleanField(db_column='AllowRateExportOnly', blank=True, null=True)  # Field name made lowercase.
    supervisorpassword = models.TextField(db_column='SupervisorPassword', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    userlayerid = models.IntegerField(db_column='userLayerId', blank=True, null=True)  # Field name made lowercase.
    userlayerreferenceid = models.BigIntegerField(db_column='userLayerReferenceId', blank=True, null=True)  # Field name made lowercase.
    allowwithdrawsmpsid = models.BooleanField(db_column='allowWithdrawSmpsId', blank=True, null=True)  # Field name made lowercase.
    allowpublishlivesmpsid = models.BooleanField(db_column='allowPublishLiveSmpsId', blank=True, null=True)  # Field name made lowercase.
    alloweditsmpsid = models.BooleanField(db_column='allowEditSmpsId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUser'


class Tbluserhistory(models.Model):
    rowid = models.AutoField(db_column='RowID', primary_key=True)  # Field name made lowercase.
    usrcode = models.IntegerField(db_column='UsrCode')  # Field name made lowercase.
    usrlevel = models.TextField(db_column='UsrLevel', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    middlename = models.CharField(db_column='MiddleName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    usrname = models.CharField(db_column='UsrName', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    usrpassword = models.TextField(db_column='UsrPassword', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    otp = models.CharField(db_column='OTP', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isotpexpired = models.BooleanField(db_column='isOTPExpired')  # Field name made lowercase.
    otpdatetimeist = models.DateTimeField(db_column='OTPDateTimeIST', blank=True, null=True)  # Field name made lowercase.
    birthdate = models.DateTimeField(db_column='BirthDate', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    add1 = models.CharField(db_column='Add1', max_length=1000, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='PinCode', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    state = models.IntegerField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    country = models.TextField(db_column='Country', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    phoneno = models.CharField(db_column='PhoneNo', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    contractorname = models.CharField(db_column='ContractorName', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(db_column='CntCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.CharField(db_column='CompanyCode', max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    countrycode = models.IntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    iscollection = models.BooleanField(db_column='IsCollection', blank=True, null=True)  # Field name made lowercase.
    isfieldofficer = models.BooleanField(db_column='IsFieldOfficer', blank=True, null=True)  # Field name made lowercase.
    allowchangepassword = models.BooleanField(db_column='AllowChangePassword', blank=True, null=True)  # Field name made lowercase.
    allowreupdatedockdata = models.BooleanField(db_column='AllowReUpdateDockData', blank=True, null=True)  # Field name made lowercase.
    isdownload = models.BooleanField(db_column='isDownload', blank=True, null=True)  # Field name made lowercase.
    downloaddatetime = models.DateTimeField(db_column='downloadDatetime', blank=True, null=True)  # Field name made lowercase.
    img = models.TextField(db_column='Img', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    allowmemberexportonly = models.BooleanField(db_column='AllowMemberExportOnly', blank=True, null=True)  # Field name made lowercase.
    allowrateexportonly = models.BooleanField(db_column='AllowRateExportOnly', blank=True, null=True)  # Field name made lowercase.
    supervisorpassword = models.TextField(db_column='SupervisorPassword', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    userlayerid = models.IntegerField(db_column='userLayerId', blank=True, null=True)  # Field name made lowercase.
    userlayerreferenceid = models.BigIntegerField(db_column='userLayerReferenceId', blank=True, null=True)  # Field name made lowercase.
    historycid = models.BigIntegerField(db_column='historyCId', blank=True, null=True)  # Field name made lowercase.
    historycdate = models.DateTimeField(db_column='historyCDate', blank=True, null=True)  # Field name made lowercase.
    allowwithdrawsmpsid = models.BooleanField(db_column='allowWithdrawSmpsId', blank=True, null=True)  # Field name made lowercase.
    allowpublishlivesmpsid = models.BooleanField(db_column='allowPublishLiveSmpsId', blank=True, null=True)  # Field name made lowercase.
    alloweditsmpsid = models.BooleanField(db_column='allowEditSmpsId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserHistory'


class Tbluserlayer(models.Model):
    userlayerid = models.IntegerField(db_column='userLayerId', primary_key=True)  # Field name made lowercase.
    userlayer = models.CharField(db_column='userLayer', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserLayer'


class Tbluserlevel(models.Model):
    userlevelcode = models.BigIntegerField(db_column='UserLevelCode', primary_key=True)  # Field name made lowercase.
    userlevel = models.TextField(db_column='UserLevel', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    userrights = models.TextField(db_column='UserRights', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserLevel'


class Tbluserright(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    userid = models.BigIntegerField(db_column='UserId')  # Field name made lowercase.
    menuid = models.IntegerField(db_column='MenuId', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.
    recordcreatedby = models.BigIntegerField(db_column='RecordCreatedBy', blank=True, null=True)  # Field name made lowercase.
    recordcreateddatetime = models.DateTimeField(db_column='RecordCreatedDatetime', blank=True, null=True)  # Field name made lowercase.
    recordmodifiedby = models.BigIntegerField(db_column='RecordModifiedBy', blank=True, null=True)  # Field name made lowercase.
    recordmodifieddatetime = models.DateTimeField(db_column='RecordModifiedDatetime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserRight'


class Tbluserrights(models.Model):
    rowid = models.AutoField(db_column='RowId', primary_key=True)  # Field name made lowercase.
    usrcode = models.IntegerField(db_column='UsrCode')  # Field name made lowercase.
    menucode = models.BigIntegerField(db_column='MenuCode')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblUserRights'


class Tblvillage(models.Model):
    villageid = models.BigIntegerField(db_column='VillageId', primary_key=True)  # Field name made lowercase.
    villagename = models.CharField(db_column='VillageName', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.CharField(db_column='Abbreviation', max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    subdistrictid = models.IntegerField(db_column='SubDistrictId', blank=True, null=True)  # Field name made lowercase.
    districtid = models.IntegerField(db_column='DistrictId', blank=True, null=True)  # Field name made lowercase.
    statecode = models.IntegerField(db_column='StateCode', blank=True, null=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=100, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblVillage'


class Tblyear(models.Model):
    yearcode = models.BigIntegerField(db_column='YearCode', primary_key=True)  # Field name made lowercase.
    othercode = models.CharField(db_column='OtherCode', max_length=128, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cycledays = models.IntegerField(db_column='CycleDays', blank=True, null=True)  # Field name made lowercase.
    desc = models.CharField(db_column='Desc', max_length=50, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblYear'


class TblSubscriberlist(models.Model):
    id = models.AutoField(primary_key=True)
    mcc_code = models.CharField(db_column='MCC_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    mpp_code = models.CharField(db_column='MPP_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    member_code = models.CharField(db_column='MEMBER_CODE', max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    addmission_fee = models.IntegerField(db_column='ADDMISSION FEE', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    share_qty = models.IntegerField(db_column='SHARE QTY', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    received_amt = models.IntegerField(db_column='RECEIVED AMT', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    amount = models.IntegerField(db_column='AMOUNT', blank=True, null=True)  # Field name made lowercase.
    share_amount = models.IntegerField(db_column='Share Amount', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    enrtydate = models.DateTimeField(db_column='ENRTYDATE', blank=True, null=True)  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_SubscriberList'


class TblProcessProductSale(models.Model):
    product_sale_id = models.AutoField(primary_key=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    collection_date = models.DateTimeField(blank=True, null=True)
    shift_code = models.IntegerField(blank=True, null=True)
    mpp_code = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    farmer_code = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    product_id = models.IntegerField(blank=True, null=True)
    product_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    product_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    credit_limit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    entry_from = models.CharField(max_length=20, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_process_product_sale'


class TblProcessShiftLock(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    bmc_code = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    mpp_code = models.CharField(max_length=10, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    collection_date = models.DateTimeField(blank=True, null=True)
    shift_code = models.IntegerField(blank=True, null=True)
    farmer_collection_lock = models.BooleanField(blank=True, null=True)
    farmer_collection_lock_time = models.DateTimeField(blank=True, null=True)
    mpp_dispatch_lock = models.BooleanField(blank=True, null=True)
    mpp_dispatch_lock_time = models.DateTimeField(blank=True, null=True)
    entry_from = models.CharField(max_length=30, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.IntegerField(blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_process_shift_lock'


class TblProperties(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    property_id = models.IntegerField()
    property_key = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    property_value = models.CharField(max_length=250, db_collation='Latin1_General_CI_AI', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_properties'


class TblReportConfig(models.Model):
    row_id = models.BigAutoField(primary_key=True)
    report_id = models.BigIntegerField()
    data_source_id = models.BigIntegerField(blank=True, null=True)
    report_name = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    config_string = models.TextField(db_collation='Latin1_General_CI_AI', blank=True, null=True)
    company_id = models.BigIntegerField(blank=True, null=True)
    record_created_by = models.BigIntegerField(blank=True, null=True)
    is_created_by_company_user = models.BooleanField(blank=True, null=True)
    record_created_datetime = models.DateTimeField(blank=True, null=True)
    record_modified_by = models.BigIntegerField(blank=True, null=True)
    is_modified_by_company_user = models.BooleanField(blank=True, null=True)
    record_modified_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tbl_report_config'


class Tblblockade(models.Model):
    rawid = models.AutoField(db_column='RawId', primary_key=True)  # Field name made lowercase.
    farmercode = models.BigIntegerField(db_column='FarmerCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='SocietyCode', blank=True, null=True)  # Field name made lowercase.
    farmerid = models.BigIntegerField(db_column='FarmerID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblblockade'


class Tblcollectionpointtype(models.Model):
    rowid = models.AutoField(db_column='rowId',primary_key=True)  # Field name made lowercase.
    id = models.IntegerField()
    collectionpointtype = models.CharField(db_column='collectionPointType', max_length=100, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblcollectionPointType'


class Tblcollectionreject(models.Model):
    rawid = models.AutoField(db_column='RawId',primary_key=True)  # Field name made lowercase.
    dumpdate = models.DateTimeField(db_column='DumpDate')  # Field name made lowercase.
    brate = models.DecimalField(db_column='BRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    crate = models.DecimalField(db_column='CRate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mrate = models.DecimalField(db_column='Mrate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    bamount = models.DecimalField(db_column='BAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    camount = models.DecimalField(db_column='CAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mamount = models.DecimalField(db_column='MAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    totalamount = models.DecimalField(db_column='TotalAmount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shift = models.CharField(db_column='Shift', max_length=1, db_collation='Latin1_General_CI_AI')  # Field name made lowercase.
    sampleid = models.IntegerField(db_column='SampleId')  # Field name made lowercase.
    rtcode = models.IntegerField(db_column='rtCode', blank=True, null=True)  # Field name made lowercase.
    soccode = models.BigIntegerField(blank=True, null=True)
    socname = models.CharField(max_length=50, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    grade = models.CharField(db_column='Grade', max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    category = models.IntegerField(db_column='Category', blank=True, null=True)  # Field name made lowercase.
    weight = models.DecimalField(db_column='Weight', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightltr = models.DecimalField(max_digits=18, decimal_places=3, blank=True, null=True)
    rcans = models.IntegerField(db_column='rCans', blank=True, null=True)  # Field name made lowercase.
    acans = models.IntegerField(db_column='aCans', blank=True, null=True)  # Field name made lowercase.
    avgfat = models.DecimalField(db_column='avgFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    avgsnf = models.DecimalField(db_column='avgSNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fat = models.DecimalField(db_column='Fat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lr = models.DecimalField(db_column='LR', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    snf = models.DecimalField(db_column='SNF', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    protein = models.DecimalField(db_column='Protein', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    lactose = models.DecimalField(db_column='Lactose', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    dockno = models.IntegerField(db_column='DockNo', blank=True, null=True)  # Field name made lowercase.
    dumptime = models.DateTimeField(db_column='DumpTime', blank=True, null=True)  # Field name made lowercase.
    testtime = models.DateTimeField(db_column='TestTime', blank=True, null=True)  # Field name made lowercase.
    did = models.IntegerField(db_column='DId', blank=True, null=True)  # Field name made lowercase.
    ddate = models.DateTimeField(db_column='DDate', blank=True, null=True)  # Field name made lowercase.
    lid = models.IntegerField(db_column='LId', blank=True, null=True)  # Field name made lowercase.
    ldate = models.DateTimeField(db_column='LDate', blank=True, null=True)  # Field name made lowercase.
    ismanuallab = models.BooleanField(blank=True, null=True)
    ismanualwt = models.BooleanField(blank=True, null=True)
    rttenkercode = models.IntegerField(blank=True, null=True)
    socpurchase = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    remarkdock = models.TextField(db_column='remarkDock', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    remarklab = models.TextField(db_column='remarkLAB', db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    lid1 = models.IntegerField(db_column='LId1', blank=True, null=True)  # Field name made lowercase.
    isupload = models.BooleanField(db_column='isUpload', blank=True, null=True)  # Field name made lowercase.
    cntcode = models.IntegerField(blank=True, null=True)
    collectioncode = models.IntegerField(db_column='CollectionCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.ForeignKey(Tblmstcompany, models.DO_NOTHING, db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    cid = models.IntegerField(db_column='CId', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MId', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.
    sadacan = models.CharField(max_length=1, db_collation='Latin1_General_CI_AI', blank=True, null=True)
    history = models.IntegerField(db_column='History', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=200, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    isskip = models.BooleanField(db_column='IsSkip', blank=True, null=True)  # Field name made lowercase.
    sampleno = models.BigIntegerField(db_column='SampleNo', blank=True, null=True)  # Field name made lowercase.
    density = models.DecimalField(db_column='Density', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    freezingpoint = models.DecimalField(db_column='FreezingPoint', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    time = models.TimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    water = models.CharField(db_column='Water', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    urea = models.CharField(db_column='Urea', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    maltodex = models.CharField(db_column='Maltodex', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    ammsulp = models.CharField(db_column='Ammsulp', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    sucrose = models.CharField(db_column='Sucrose', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    abnormal = models.CharField(db_column='Abnormal', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    badsample = models.CharField(db_column='BadSample', max_length=32, db_collation='Latin1_General_CI_AI', blank=True, null=True)  # Field name made lowercase.
    rate = models.DecimalField(db_column='Rate', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    weightrejected = models.DecimalField(db_column='WeightRejected', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    isprocessed = models.BooleanField(db_column='IsProcessed', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblcollectionReject'


class Tblsocietymapping(models.Model):
    rowid = models.AutoField(db_column='RowId',primary_key=True)  # Field name made lowercase.
    usercode = models.BigIntegerField(db_column='UserCode', blank=True, null=True)  # Field name made lowercase.
    centercode = models.BigIntegerField(db_column='CenterCode', blank=True, null=True)  # Field name made lowercase.
    societycode = models.BigIntegerField(db_column='SocietyCode', blank=True, null=True)  # Field name made lowercase.
    companycode = models.BigIntegerField(db_column='CompanyCode', blank=True, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', blank=True, null=True)  # Field name made lowercase.
    cid = models.BigIntegerField(db_column='CID', blank=True, null=True)  # Field name made lowercase.
    cdate = models.DateTimeField(db_column='CDate', blank=True, null=True)  # Field name made lowercase.
    mid = models.BigIntegerField(db_column='MID', blank=True, null=True)  # Field name made lowercase.
    mdate = models.DateTimeField(db_column='MDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tblsocietyMapping'


class Tempcompanysettinngs(models.Model):
    setting_id = models.BigIntegerField(db_column='Setting_Id',primary_key=True)  # Field name made lowercase.
    company_id = models.BigIntegerField(db_column='Company_Id', blank=True, null=True)  # Field name made lowercase.
    isfarmercodechanged = models.BooleanField(db_column='IsFarmerCodeChanged', blank=True, null=True)  # Field name made lowercase.
    cuserid = models.BigIntegerField(db_column='cUserId', blank=True, null=True)  # Field name made lowercase.
    cdatetime = models.DateTimeField(db_column='cDateTime', blank=True, null=True)  # Field name made lowercase.
    muserid = models.BigIntegerField(db_column='mUserId', blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.DateTimeField(db_column='mDateTime', blank=True, null=True)  # Field name made lowercase.
    allow_society_active = models.BooleanField(db_column='Allow_Society_Active', blank=True, null=True)  # Field name made lowercase.
    minbufffat = models.DecimalField(db_column='minBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbufffat = models.DecimalField(db_column='maxBuffFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowfat = models.DecimalField(db_column='minCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowfat = models.DecimalField(db_column='maxCowFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffsnf = models.DecimalField(db_column='minBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffsnf = models.DecimalField(db_column='maxBuffSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowsnf = models.DecimalField(db_column='minCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowsnf = models.DecimalField(db_column='maxCowSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixfat = models.DecimalField(db_column='minMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixfat = models.DecimalField(db_column='maxMixFat', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixsnf = models.DecimalField(db_column='minMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixsnf = models.DecimalField(db_column='maxMixSnf', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minmixclr = models.DecimalField(db_column='minMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxmixclr = models.DecimalField(db_column='maxMixClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    minbuffclr = models.DecimalField(db_column='minBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxbuffclr = models.DecimalField(db_column='maxBuffClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mincowclr = models.DecimalField(db_column='minCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    maxcowclr = models.DecimalField(db_column='maxCowClr', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    israngeexclusive = models.BooleanField(db_column='isRangeExclusive', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tempcompanysettinngs'
