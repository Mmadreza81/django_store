from .cart import Cart

# برای نشان دادن سبد خرید در هر صفحه ای
def cart(request):
    return {'cart': Cart(request)}
