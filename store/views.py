import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View
# PDF GENERATION
from django.template.loader import get_template
from .utils import render_to_pdf

from user.models import UserProfile

from .forms import CheckoutForm, CouponForm, PaymentForm, RefundForm
from .models import *
from .models import District, SeedProduct


stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


class TreeSeedListView(ListView):
    model = SeedProduct
    queryset = SeedProduct.objects.filter(available=True)
    template_name = 'store/store.html'
    context_object_name = 'tree_seeds'
    paginate_by = 20  # that is all it takes to add pagination in a Class Based View

    # def get_context_data(self, **kwargs):
    #     context = super(BlogPostListView, self).get_context_data(**kwargs)
    #     context['categories'] =  Category.objects.all()
    #     context['blog_featured'] = BlogPost.objects.filter(featured=True)
    #     return context


class TreeSeedDetailView(DetailView):
    model = SeedProduct
    queryset = SeedProduct.objects.filter(available=True)
    template_name = 'store/product.html'
    context_object_name = 'product'
    # print(request)

    def get_context_data(self, **kwargs):
        context = super(TreeSeedDetailView, self).get_context_data(**kwargs)
        context['related'] = SeedProduct.objects.filter(available=True)
        context['districts'] = District.objects.all()
        return context


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': SeedProduct.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "store/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("store:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:

                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('store:checkout')
                else:

                    shipping_street_address = form.cleaned_data.get(
                        'shipping_street_address')
                    shipping_city = form.cleaned_data.get(
                        'shipping_city')
                    shipping_district = form.cleaned_data.get(
                        'shipping_district')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    first_name = form.cleaned_data.get(
                        'first_name')
                    last_name = form.cleaned_data.get(
                        'last_name')
                    # shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([first_name,last_name, shipping_street_address, shipping_country, shipping_city, shipping_district]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_street_address,
                            city=shipping_city,
                            district=shipping_district,
                            country=shipping_country,
                            address_type='S',
                            first_name=first_name,
                            last_name=last_name
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect('store:checkout')

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')

                if use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('store:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_street_address = form.cleaned_data.get(
                        'billing_street_address')
                    billing_city = form.cleaned_data.get(
                        'billing_city')
                    billing_district = form.cleaned_data.get(
                        'billing_district')
                    address_email = form.cleaned_data.get(
                        'email')

                #

                    if is_valid_form([billing_street_address, billing_city, billing_district, address_email]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_street_address,
                            city=billing_city,
                            district=billing_district,
                            secondary_email=address_email,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('store:payment', payment_option='stripe')
                elif payment_option == 'M':
                    return redirect('store:payment', payment_option='momopay')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('store:checkout')
            else:
                messages.info(self.request, 'Fill out the form to proceed')
                return redirect('store:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("store:order-summary")

@method_decorator(login_required, name='dispatch')
class PaymentView(View):
    def get(self, *args, **kwargs):
        payment_option = kwargs['payment_option']
        if payment_option == 'stripe':
            messages.info(self.request, 'Sorry, we do not accept payment with stripe yet.')
            return redirect('home')
            # order = Order.objects.get(user=self.request.user, ordered=False)
            # if order.shipping_address:
            #     context = {
            #         'order': order,
            #         'DISPLAY_COUPON_FORM': False,
            #         'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
            #     }
            #     userprofile = self.request.user.userprofile
            #     if userprofile.one_click_purchasing:
            #         # fetch the users card list
            #         cards = stripe.Customer.list_sources(
            #             userprofile.stripe_customer_id,
            #             limit=3,
            #             object='card'
            #         )
            #         card_list = cards['data']
            #         if len(card_list) > 0:
            #             # update the context with the default card
            #             context.update({
            #                 'card': card_list[0]
            #             })
            #     return render(self.request, "store/payment.html", context)
            # else:
            #     messages.warning(
            #         self.request, "You have not added a shipping address")
            #     return redirect("store:checkout")
        elif payment_option == 'momopay':
            messages.info(self.request, 'Sorry, we do not accept MOMO PAY yet.')
            return redirect('home')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if self.request.method == 'POST':
            token = self.request.POST.get('stripeToken')
            save = self.request.POST.get('save')
            use_default = self.request.POST.get('use_default')
            print(token)
            print(token)
            print(order.get_total())

            # HANDLING BILLING ADDRESS
            # first_name = form.cleaned_data.get('first_name')
            # last_name = form.cleaned_data.get('last_name')
            # street_address = form.cleaned_data.get('street_address')
            # city = form.cleaned_data.get('city')
            # district = form.cleaned_data.get('district')
            # mobile = form.cleaned_data.get('mobile')
            # post_code = form.cleaned_data.get('postal_code')
            # email = form.cleaned_data.get('email')

            # billing_address = Address(
            #     user=self.request.user,
            #     street_address=street_address,
            #     city=city,
            #     district=district,
            #     address_type='B',
            #     postal_code=post_code,
            # )
            # billing_address.save()

            # order.billing_address = billing_address
            # order.save()
            # print(email)

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100 / 924)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")

                return HttpResponse(f'<h1>Your Order {order.ref-code} is being processed</h1>')

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = SeedProduct
    paginate_by = 10
    template_name = "store/store.html"
    context_object_name = 'tree_seeds'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        # context['recent'] = SeedProduct.objects.filter(available=True).order_by('-created_on')[:10]

        return context

@method_decorator(login_required, name='dispatch')
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'store/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class SeedProductDetailView(DetailView):
    model = SeedProduct
    template_name = "store/product.html"
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super(SeedProductDetailView, self).get_context_data(**kwargs)
        context['related'] = SeedProduct.objects.filter(available=True)
        context['new_products'] = SeedProduct.objects.filter(available=True).order_by('-created_on')[:5]
        return context


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("store:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("store:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("store:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("store:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("store:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("store:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("store:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("store:checkout")

@method_decorator(login_required, name='dispatch')
class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("store:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("store:checkout")

@method_decorator(login_required, name='dispatch')
class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("store:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("store:request-refund")


def generate_card(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    if item:
        context = {'item': item}
        return render(request, 'store/card.html', context)
    else:
        return redirect("store:order-summary")


def download_pdf(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    if item:
        context ={
            'item': item
        }
        template_name = 'store/card_pdf.html'
        pdf = render_to_pdf(template_name, context)
        return HttpResponse(pdf, content_type='application/pdf')

    else:
        messages.info(request, 'This product does not exist')
        return redirect('home')
