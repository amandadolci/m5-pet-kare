from rest_framework.views import APIView, Request, Response, status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Pet
from .serializers import PetSerializer
from groups.models import Group
from traits.models import Trait


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        trait = request.query_params.get('trait')
        if trait:
            pets = Pet.objects.filter(traits__name__iexact=trait)
        else:
            pets = Pet.objects.all()

        result = self.paginate_queryset(pets, request)
        serializer = PetSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop('group')
        traits_data = serializer.validated_data.pop('traits')
        try:
            group = Group.objects.get(
                scientific_name__iexact=group_data['scientific_name']
                )
        except Group.DoesNotExist:
            group = Group.objects.create(**group_data)

        created_pet = Pet.objects.create(
            **serializer.validated_data,
            group=group,
            )

        for trait_data in traits_data:
            try:
                trait = Trait.objects.get(name__iexact=trait_data['name'])
            except Trait.DoesNotExist:
                trait = Trait.objects.create(**trait_data)
            created_pet.traits.add(trait)

        serializer = PetSerializer(created_pet)
        return Response(serializer.data, status.HTTP_201_CREATED)


class PetDetailView(APIView):
    def get(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)
        return Response(serializer.data)

    def patch(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop('group', None)
        traits_data = serializer.validated_data.pop('traits', None)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        if group_data:
            try:
                group = Group.objects.get(
                    scientific_name__iexact=group_data['scientific_name']
                    )
            except Group.DoesNotExist:
                group = Group.objects.create(**group_data)
            pet.group = group

        if traits_data:
            pet.traits.clear()
            for trait_data in traits_data:
                try:
                    trait = Trait.objects.get(
                        name__iexact=trait_data['name']
                        )
                except Trait.DoesNotExist:
                    trait = Trait.objects.create(**trait_data)

                pet.traits.add(trait)
        pet.save()

        serializer = PetSerializer(pet)
        return Response(serializer.data)

    def delete(self, request: Request, pet_id: int) -> Response:
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
