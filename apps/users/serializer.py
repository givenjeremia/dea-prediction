
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import Profile
# from django.db import IntegrityError



# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username','first_name', 'password', 'email']

#     def create(self, validated_data):
#         password = validated_data.pop('password', None)

#         try:
#             user = User.objects.create(**validated_data)
#         except IntegrityError:
#             raise serializers.ValidationError({'detail': 'Username or email already exists.'})

#         if password is not None:
#             user.set_password(password)
#             user.save()

#         return user

# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = '__all__'
