from rest_framework import serializers
from .models import Tblfarmercollection

class TblfarmercollectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tblfarmercollection
        fields = ['rowid', 'dumpdate', 'dumptime','shift','weight', 'fat',  'snf','totalamount', 'member_other_code', ]
        
        def to_representation(self, instance):
            representation = super().to_representation(instance)
            # Format numerical fields to two decimal places
            for field in ['weight', 'fat', 'snf', 'totalamount']:
                if representation.get(field) is not None:
                    representation[field] = format(float(representation[field]), '.2f')
            return representation
