from rest_framework import serializers
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer

SEX_CHOICES = ('Male', 'Female', 'Not Informed')


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.ChoiceField(
        choices=SEX_CHOICES,
        required=False
    )
    group = GroupSerializer()
    traits = TraitSerializer(many=True)
