from django.shortcuts import render
from django.conf import settings
import requests
from django.contrib.auth.models import User,Group

from users.serializer import ProfileSerializer
from management.models import UnitWorks,Departements


# Create your views here.
def getRolesAndFormApi(username):
    url = f"{settings.URL_BRIDGE}/profile/{username}"
    print(url)
    token = settings.BRIDGE_TOKEN
    headers = {
        'Authorization': token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("success")
        bridge = response.json()
        result = bridge['results']
        # Get Satuan Kerja
        satuan_kerja = result['satuan_kerja_nama']
        # Get Name
        nama = result['nama']
        # Department Name
        departemen_name = result['structure']['organizations']['divisions']['departments']['satker_name']
            
        # Fetch UnitWork and Department
        unit_work = UnitWorks.objects.filter(name__iexact=satuan_kerja).first()
        departement = Departements.objects.filter(unit_work=unit_work.id, name__iexact=departemen_name).first()
        print('---==-----')
        print(departemen_name)
        print(departement)
        print(unit_work)   
        role_coofis = result['roles_coofis']
        key = next((i for i, item in enumerate(role_coofis) if item['service_name'] == 'website_service'), None)
    
    
        print(role_coofis)
        print(key)
        if key is not None:
            state = role_coofis[key]['state']
            user = User.objects.filter(username=username).first()
            print(state)
            if state == "PPID.KKP":
                print('Role data found')
                try:
                    group = Group.objects.get(name='Super Admin')
                except Group.DoesNotExist:
                    group = Group.objects.create(name='Super Admin')
                    print('Group "ukpbjs" created')
                user.groups.add(group)
                user.save()
            elif state == "PPID.P.PUSAT":
                print('Role data found')
                try:
                    group = Group.objects.get(name='UPP')
                except Group.DoesNotExist:
                    group = Group.objects.create(name='UPP')
                    print('Group "ukpbjs" created')
                user.groups.add(group)
                user.save()
                print(user)
            elif state == "PPID.P.TEKNIS":
                print('Role data found')
                try:
                    group = Group.objects.get(name='UPT')
                except Group.DoesNotExist:
                    group = Group.objects.create(name='UPT')
                    print('Group "ukpbjs" created')
                user.groups.add(group)
                user.save()
                print(user)

            # ADD USER PROFILE
            profile = {
                'departement': departement.id if departement else None ,
                'unit_work': unit_work.id,
                'user':user.id 
            }
            serializer = ProfileSerializer(data=profile)
            if serializer.is_valid():
                serializer.save()
            return True
        else:
            return False
    return False