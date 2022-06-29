# Generated by Django 4.0.4 on 2022-06-05 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BankSystem', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('no', models.CharField(default='', max_length=10, primary_key=True, serialize=False, verbose_name='payout编号')),
                ('date', models.DateField(default='2022-5-16', verbose_name='支付日期')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=14, verbose_name='金额')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BankSystem.loan', verbose_name='所属贷款')),
            ],
        ),
    ]
