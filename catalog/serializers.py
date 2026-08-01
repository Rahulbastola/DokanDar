from rest_framework import serializers

from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['product', 'user', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='created_by.username', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'stock', 'category', 'category_name',
            'vendor_name', 'avg_rating', 'review_count', 'thumbnail', 'is_active', 'created_at',
        ]

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if not first_image:
            return None
        request = self.context.get('request')
        url = first_image.image.url
        return request.build_absolute_uri(url) if request else url


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='created_by.username', read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock', 'category', 'category_name',
            'created_by', 'vendor_name', 'is_active', 'images', 'uploaded_images',
            'reviews', 'avg_rating', 'review_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by']

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images', [])
        validated_data['created_by'] = self.context['request'].user
        product = Product.objects.create(**validated_data)
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop('uploaded_images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for image in images:
            ProductImage.objects.create(product=instance, image=image)
        return instance
