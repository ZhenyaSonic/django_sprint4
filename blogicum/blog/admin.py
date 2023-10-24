from django.contrib import admin

from blog.models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'category',
        'location',
        'author',
        'pub_date'
    )
    list_editable = (
        'is_published',
        'pub_date',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post'
    )


admin.site.register(Location)
