
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_list_or_404, get_object_or_404

from utils.recipes.pagination import  make_pagination
from recipes.models import Recipe


PER_PAGE = 9

def home(request):
    recipes = Recipe.objects.filter(is_published=True).order_by('-id')
    page_obj, pagination = make_pagination(request, recipes, PER_PAGE, 4)
    context = {
        'recipes': page_obj,
        'pages': pagination
    }
    return render(request, 'recipes/pages/home.html', context)

def recipe(request, id):
    recipe = get_object_or_404(Recipe, pk=id, is_published=True)
    return render(request, 'recipes/pages/recipe-view.html', context={
        'recipe': recipe,
        'is_detail_page': True,
    })

def category(request, category_id):
    recipes = get_list_or_404(Recipe.objects.filter(category__id=category_id, is_published=True).order_by('-id'))
    page_obj, pagination = make_pagination(request, recipes, PER_PAGE, 4)

    context = {
        'recipes': page_obj,
        'title': f'{recipes[0].category.name} - Category | ',
        'pages': pagination
    }
    return render(request, 'recipes/pages/category.html', context)

def search(request):
    search_term = request.GET.get('q', '').strip()
    
    if not search_term:
        raise Http404()
    
    recipes = Recipe.objects.filter(
        Q(
            Q(title__icontains=search_term) |
            Q(description__icontains=search_term)
        ),
        is_published=True,
    ).order_by('-id')
    page_obj, pagination = make_pagination(request, recipes, PER_PAGE, 4)
        
    context = {
        'page_title': f'Search for "{search_term}" | ',
        'search_term': search_term,
        'recipes': page_obj,
        'pages': pagination,
        'additional_url_query': f'&q={search_term}',
    }
    return render(request, 'recipes/pages/search.html', context)
