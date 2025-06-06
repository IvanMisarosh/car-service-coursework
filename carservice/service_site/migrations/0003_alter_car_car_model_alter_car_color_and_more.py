# Generated by Django 4.2.20 on 2025-05-13 10:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_site', '0002_alter_car_vin_alter_employee_employee_position_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='car_model',
            field=models.ForeignKey(db_column='CarModelID', on_delete=django.db.models.deletion.PROTECT, to='service_site.carmodel'),
        ),
        migrations.AlterField(
            model_name='car',
            name='color',
            field=models.ForeignKey(db_column='ColorID', on_delete=django.db.models.deletion.PROTECT, to='service_site.color'),
        ),
        migrations.AlterField(
            model_name='car',
            name='customer',
            field=models.ForeignKey(db_column='CustomerID', on_delete=django.db.models.deletion.PROTECT, related_name='cars', to='service_site.customer'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='station',
            field=models.ForeignKey(db_column='StationID', on_delete=django.db.models.deletion.PROTECT, to='service_site.station'),
        ),
        migrations.AlterField(
            model_name='partinstation',
            name='part',
            field=models.ForeignKey(db_column='PartID', on_delete=django.db.models.deletion.PROTECT, to='service_site.part'),
        ),
        migrations.AlterField(
            model_name='partinstation',
            name='station',
            field=models.ForeignKey(db_column='StationID', on_delete=django.db.models.deletion.PROTECT, to='service_site.station'),
        ),
        migrations.AlterField(
            model_name='procurementorder',
            name='employee',
            field=models.ForeignKey(db_column='EmployeeID', on_delete=django.db.models.deletion.PROTECT, to='service_site.employee'),
        ),
        migrations.AlterField(
            model_name='procurementorder',
            name='supplier',
            field=models.ForeignKey(db_column='SupplierID', on_delete=django.db.models.deletion.PROTECT, to='service_site.supplier'),
        ),
        migrations.AlterField(
            model_name='procurementunit',
            name='part',
            field=models.ForeignKey(db_column='PartID', on_delete=django.db.models.deletion.PROTECT, to='service_site.part'),
        ),
        migrations.AlterField(
            model_name='procurementunit',
            name='procurement_order',
            field=models.ForeignKey(db_column='ProcurementOrderID', on_delete=django.db.models.deletion.PROTECT, related_name='units', to='service_site.procurementorder'),
        ),
        migrations.AlterField(
            model_name='providedservice',
            name='visit_service',
            field=models.OneToOneField(db_column='VisitServiceID', on_delete=django.db.models.deletion.PROTECT, related_name='provided_service', to='service_site.visitservice'),
        ),
        migrations.AlterField(
            model_name='requiredpart',
            name='part_in_station',
            field=models.ForeignKey(db_column='PartInStationID', on_delete=django.db.models.deletion.PROTECT, to='service_site.partinstation'),
        ),
        migrations.AlterField(
            model_name='requiredpart',
            name='provided_service',
            field=models.ForeignKey(db_column='ProvidedServiceID', on_delete=django.db.models.deletion.PROTECT, related_name='required_parts', to='service_site.providedservice'),
        ),
        migrations.AlterField(
            model_name='storageplacement',
            name='part_in_station',
            field=models.ForeignKey(db_column='PartInStationID', on_delete=django.db.models.deletion.PROTECT, to='service_site.partinstation'),
        ),
        migrations.AlterField(
            model_name='storageplacement',
            name='procurement_unit',
            field=models.ForeignKey(db_column='ProcurementUnitID', on_delete=django.db.models.deletion.PROTECT, related_name='placements', to='service_site.procurementunit'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='car',
            field=models.ForeignKey(db_column='CarID', on_delete=django.db.models.deletion.PROTECT, related_name='visits', to='service_site.car'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='employee',
            field=models.ForeignKey(db_column='EmployeeID', on_delete=django.db.models.deletion.PROTECT, to='service_site.employee'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='visit_status',
            field=models.ForeignKey(db_column='VisitStatusID', on_delete=django.db.models.deletion.PROTECT, to='service_site.visitstatus'),
        ),
        migrations.AlterField(
            model_name='visitservice',
            name='service',
            field=models.ForeignKey(db_column='ServiceID', on_delete=django.db.models.deletion.PROTECT, to='service_site.service'),
        ),
        migrations.AlterField(
            model_name='visitservice',
            name='visit',
            field=models.ForeignKey(db_column='VisitID', on_delete=django.db.models.deletion.PROTECT, related_name='visit_services', to='service_site.visit'),
        ),
    ]
