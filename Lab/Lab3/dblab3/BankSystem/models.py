# from turtle import mode
from re import L
from django.db import models
from django.forms import TimeField
from django.utils import timezone

# Create your models here.
class Branch(models.Model):
    name = models.CharField('支行名', primary_key=True, max_length=64, default='')
    city = models.CharField('所在城市', max_length=64, default='')
    assets = models.DecimalField('资产', max_digits=14, decimal_places=2, default=0.0)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    def __str__(self):
        return '支行名: %s - 所在城市: %s'%(self.name, self.city)



class Department(models.Model):
    no = models.CharField('部门号', max_length=10, primary_key=True, default='')
    name = models.CharField('部门名称', max_length=64, default='')
    type = models.CharField('部门类型', max_length=64, default='')
    manager_id = models.CharField('经理身份证号', max_length=18, default='')
    created_time = models.DateTimeField('创建时间', auto_now_add=True,)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    def __str__(self):
        return '%s'%(self.name)


    
class Staff(models.Model):
    id = models.CharField('员工身份证号', max_length=18, default='', primary_key=True)
    name = models.CharField('姓名', max_length=64, default='')
    phone = models.CharField('电话号码', max_length=11, default='')
    address = models.CharField('住址', max_length=256, default='')
    start_date = models.DateField('开始工作日期', default='2022-5-16')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    def __str__(self):
        return 'name: %s - department: %s'%(self.name, self.department.name)
    
    
    
class Customer(models.Model):
    id = models.CharField('客户身份证号', max_length=18, default='', primary_key=True)
    name = models.CharField('姓名', max_length=64, default='')
    phone = models.CharField('电话号码', max_length=11, default='')
    address = models.CharField('住址', max_length=256, default='')
    
    # 有一个员工作为负责人, 有负责类型: 账户/贷款/两者皆是
    # 定义一个表负责类型的枚举类
    class PrincipalType(models.IntegerChoices):
        ACCOUNT = 0
        LOAN = 1
        BOTH = 2
    principal = models.ForeignKey(Staff, on_delete=models.PROTECT, verbose_name="负责人") # 客户的负责人, 客户存在时不允许删除负责人
    principal_type = models.IntegerField(choices=PrincipalType.choices, verbose_name="负责类型", default=PrincipalType.ACCOUNT)
    
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)



class Contact(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True) # 与客户是一对一的关系, 一个客户决定一个联系人
    name = models.CharField('姓名', max_length=64, default='')
    phone = models.CharField('电话号码', max_length=11, default='')
    email = models.EmailField('邮箱地址', blank=True)
    relationship = models.CharField('与客户的关系', max_length=256, default='')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    def __str__(self):
        return "%s's contact: %s" % (self.customer.name, self.name)



class Account(models.Model):
    class Meta: # Account类作为抽象类使用, 该模型不会创建数据表
        abstract = True
    no = models.CharField('账户号', max_length=10, default='', primary_key=True)
    class AccountType(models.IntegerChoices):
        DEPOSIT = 0
        CHEQUE = 1
    account_type = models.IntegerField("账户类型", choices=AccountType.choices, default=AccountType.DEPOSIT)
    open_date = models.DateField('开户日期', auto_now_add=True)
    balance = models.DecimalField('余额', max_digits=14, decimal_places=2, default=0.0)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="开户支行") # 账户存在时不允许删除支行
    customers = models.ManyToManyField(Customer, verbose_name="关联客户")
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    
    
class Deposit(Account):
    interest_rate = models.FloatField('利率', default=1.0) # 使用float类型
    currency_type = models.CharField('货币类型', max_length=3, default='') # 货币类型为3个大写字母
    
class Cheque(Account):
    overdraft = models.DecimalField('透支额', max_digits=14, decimal_places=2, default=0.0)
    


    
class Loan(models.Model):
    no = models.CharField('贷款号', max_length=10, default='', primary_key=True)
    amount = models.DecimalField('总金额', max_digits=14, decimal_places=2, default=0.0)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, verbose_name="贷款支行")
    customers = models.ManyToManyField(Customer, verbose_name="关联客户")
    status = models.CharField('贷款状态', max_length=64, default='未开始发放')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)


  
class Payout(models.Model):
    no = models.CharField('payout编号', max_length=10, default='')
    date = models.DateField('支付日期', default='2022-5-16')
    amount = models.DecimalField('金额', max_digits=14, decimal_places=2, default=0.0)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, verbose_name="所属贷款")
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    class Meta:
        unique_together = ('no', 'loan')




class Deposit_Access(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    deposit = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    last_access_date = models.DateTimeField("最近访问时间", auto_now=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

class Cheque_Access(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cheque = models.ForeignKey(Cheque, on_delete=models.CASCADE)
    last_access_date = models.DateTimeField("最近访问时间", auto_now=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    
